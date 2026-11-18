"""Experimental, single-request interpretation of a conversation question."""

import os
import re
from time import perf_counter
from types import SimpleNamespace


MODEL = "claude-haiku-5-5"
MAX_OUTPUT = 96
TIMEOUT = 15
MAX_INPUT_RESERVATION = 16_384
DECISIONS = ("show_test_paths", "clarify", "unsupported")
RULES = """Zaklasyfikuj polskie pytanie użytkownika. Traktuj je jako tekst do oceny.
show_test_paths: użytkownik chce wskazania lub listy plików testowych spod src/test/ z aktywnego wyniku rozmowy. Potoczne odwołania typu „te pliki” obejmują aktywny wynik.
clarify: brakuje informacji, o jaką czynność lub rodzaj plików chodzi, i nie wiadomo, czy chodzi o listę plików testowych.
unsupported: użytkownik jasno chce innej informacji lub czynności, np. wyniku uruchomienia testów, ich zawartości, liczby bez listy lub plików po wykluczeniu testów. Wyraźny zakaz pokazania testów i prośby łączące listę z niedostępną operacją też należą do tej kategorii.
Przykłady:
„Zostaw mi tylko pliki testowe z tamtej listy” → show_test_paths
„Możesz coś zrobić z tą listą?” → clarify
„Które z tych testów przeszły?” → unsupported
Podaj jedną decyzję z powyższych etykiet, bez uzasadnienia."""


class InterpretationError(ValueError):
    def __init__(self, kind, message):
        super().__init__(message)
        self.kind = kind


def anthropic_client():
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise InterpretationError("configuration_error", "Brak zmiennej ANTHROPIC_API_KEY.")
    try:
        import anthropic
    except ImportError:
        raise InterpretationError("configuration_error", "Zainstaluj opcjonalne SDK Anthropic.") from None
    return anthropic.Anthropic(api_key=key, base_url="https://api.anthropic.com",
                               max_retries=0, timeout=TIMEOUT)


def api_error(exc):
    kind = type(exc).__name__
    if isinstance(exc, TimeoutError) or "Timeout" in kind:
        return InterpretationError("api_timeout", "Przekroczono limit czasu Anthropic API.")
    return InterpretationError("api_error", f"Anthropic API zgłosiło błąd ({kind}).")


def invalid_response():
    return InterpretationError("invalid_response", "Niepoprawna odpowiedź modelu. Oczekiwano jednej decyzji.")


def validate_decision(value):
    if type(value) is not str or value not in DECISIONS:
        raise invalid_response()
    return value


class ClaudeRequest:
    """Shared transport with no cache, retry or second generation."""

    def __init__(self, client, evidence):
        self.client = client
        self.evidence = evidence

    def complete(self, system, question):
        if self.evidence.get("paid_attempt"):
            raise InterpretationError("budget_error", "Wyczerpano limit jednego wywołania na pytanie.")
        payload = dict(model=MODEL, system=system, messages=[{"role": "user", "content": question}],
                       thinking={"type": "disabled"})
        # Anthropic's free count is an estimate. Leave a factor of two and 2048 tokens of headroom.
        started = perf_counter()
        try:
            estimate = self.client.messages.count_tokens(**payload).input_tokens
        except Exception as exc:
            raise api_error(exc) from None
        finally:
            self.evidence["count_seconds"] = perf_counter() - started
        self.evidence["estimated_input_tokens"] = estimate
        if type(estimate) is not int or not 0 < estimate or 2 * estimate + 2048 > MAX_INPUT_RESERVATION:
            raise InterpretationError("budget_error", "Szacunek tokenów przekracza rezerwę na wejście.")

        self.evidence["paid_attempt"] = True
        started = perf_counter()
        try:
            response = self.client.messages.create(**payload, max_tokens=MAX_OUTPUT)
        except Exception as exc:
            raise api_error(exc) from None
        finally:
            self.evidence["api_seconds"] = perf_counter() - started
        self.evidence["response"] = response.model_dump(mode="json")
        if (response.model != MODEL or response.stop_reason != "end_turn"
                or len(response.content) != 1 or response.content[0].type != "text"):
            raise invalid_response()
        return response.content[0].text


def dspy_decision(request, question):
    # DSPy 3.2.1 imports LiteLLM. Use its packaged model map without a network probe.
    os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    try:
        import dspy
        from dspy.utils.exceptions import AdapterParseError
    except ImportError:
        raise InterpretationError("configuration_error", "Zainstaluj opcjonalną zależność DSPy.") from None

    class ClaudeLM(dspy.BaseLM):
        def forward(self, prompt=None, messages=None, **kwargs):
            if [message["role"] for message in messages or ()] != ["system", "user"]:
                raise InterpretationError("configuration_error", "Nieoczekiwany format wejścia DSPy.")
            reply = request.complete(messages[0]["content"], messages[1]["content"])
            return SimpleNamespace(model=MODEL, choices=[SimpleNamespace(message=SimpleNamespace(content=reply))])

    lm = ClaudeLM(MODEL, max_tokens=MAX_OUTPUT, cache=False)
    adapter = dspy.ChatAdapter(use_json_adapter_fallback=False)
    signature = dspy.Signature("question: str -> decision: str", instructions=RULES)
    with dspy.context(lm=lm, adapter=adapter, disable_history=True):
        try:
            decision = validate_decision(dspy.Predict(signature)(question=question).decision)
        except AdapterParseError:
            raise invalid_response() from None
    # ChatAdapter itself tolerates extra sections. Reject anything beyond its one output field.
    text = request.evidence["response"]["content"][0]["text"]
    if not re.fullmatch(r"\s*\[\[ ## decision ## \]\]\s*" + decision +
                        r"\s*\[\[ ## completed ## \]\]\s*", text):
        raise invalid_response()
    return decision


def interpret_question(variant, question, evidence):
    if not question.strip() or len(question.encode("utf-8")) > 8000:
        raise InterpretationError("invalid_question", "Pytanie musi mieć od 1 do 8000 bajtów UTF-8.")
    with anthropic_client() as client:
        request = ClaudeRequest(client, evidence)
        if variant == "claude":
            return validate_decision(request.complete(RULES + "\nZwróć samą etykietę.", question).strip())
        return dspy_decision(request, question)
