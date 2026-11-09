import FastChecker
import ProofTiming
set_option maxRecDepth 100000
set_option maxHeartbeats 0
namespace ChromiumFast
open RepoProof
def pathBlock0 : Array String := #[
  "android_webview/common/mojom/frame.mojom",
  "android_webview/common/mojom/render_message_filter.mojom",
  "android_webview/common/mojom/renderer.mojom",
  "ash/public/mojom/accelerator_actions.mojom",
  "ash/public/mojom/accelerator_configuration.mojom",
  "ash/public/mojom/accelerator_info.mojom",
  "ash/public/mojom/accelerator_keys.mojom",
  "ash/public/mojom/hid_preserving_bluetooth_state_controller.mojom",
  "ash/public/mojom/input_device_settings.mojom",
  "ash/public/mojom/wallpaper.mojom",
  "ash/style/mojom/color_scheme.mojom",
  "ash/system/diagnostics/mojom/input.mojom",
  "ash/webui/annotator/mojom/untrusted_annotator.mojom",
  "ash/webui/annotator/public/mojom/annotator_structs.mojom",
  "ash/webui/boca_receiver_app_ui/mojom/boca_receiver.mojom",
  "ash/webui/boca_ui/mojom/boca.mojom",
  "ash/webui/camera_app_ui/camera_app_helper.mojom",
  "ash/webui/camera_app_ui/events_sender.mojom",
  "ash/webui/camera_app_ui/ocr.mojom",
  "ash/webui/camera_app_ui/pdf_builder.mojom",
  "ash/webui/camera_app_ui/types.mojom",
  "ash/webui/color_internals/mojom/color_internals.mojom",
  "ash/webui/common/mojom/accelerator_fetcher.mojom",
  "ash/webui/common/mojom/accessibility_features.mojom",
  "ash/webui/common/mojom/sea_pen.mojom",
  "ash/webui/common/mojom/sea_pen_generated.mojom",
  "ash/webui/common/mojom/shortcut_input_provider.mojom",
  "ash/webui/common/mojom/webui_syslog_emitter.mojom",
  "ash/webui/demo_mode_app_ui/mojom/demo_mode_app_untrusted_ui.mojom",
  "ash/webui/diagnostics_ui/mojom/input_data_provider.mojom",
  "ash/webui/diagnostics_ui/mojom/network_health_provider.mojom",
  "ash/webui/diagnostics_ui/mojom/system_data_provider.mojom",
  "ash/webui/diagnostics_ui/mojom/system_routine_controller.mojom",
  "ash/webui/eche_app_ui/mojom/eche_app.mojom",
  "ash/webui/file_manager/mojom/file_manager.mojom",
  "ash/webui/files_internals/mojom/files_internals.mojom",
  "ash/webui/firmware_update_ui/mojom/firmware_update.mojom",
  "ash/webui/focus_mode/mojom/focus_mode.mojom",
  "ash/webui/graduation/mojom/graduation_ui.mojom",
  "ash/webui/growth_internals/growth_internals.mojom",
  "ash/webui/help_app_ui/help_app_ui.mojom",
  "ash/webui/help_app_ui/search/search.mojom",
  "ash/webui/mall/mall_ui.mojom",
  "ash/webui/media_app_ui/media_app_ui.mojom",
  "ash/webui/media_app_ui/media_app_ui_untrusted.mojom",
  "ash/webui/os_feedback_ui/mojom/os_feedback_ui.mojom",
  "ash/webui/personalization_app/mojom/personalization_app.mojom",
  "ash/webui/personalization_app/search/search.mojom",
  "ash/webui/projector_app/mojom/untrusted_projector.mojom",
  "ash/webui/projector_app/public/mojom/projector_types.mojom",
  "ash/webui/recorder_app_ui/mojom/recorder_app.mojom",
  "ash/webui/sample_system_web_app_ui/mojom/sample_system_web_app_shared_ui.mojom",
  "ash/webui/sample_system_web_app_ui/mojom/sample_system_web_app_ui.mojom",
  "ash/webui/sample_system_web_app_ui/mojom/sample_system_web_app_untrusted_ui.mojom",
  "ash/webui/sanitize_ui/mojom/sanitize_ui.mojom",
  "ash/webui/scanner_feedback_ui/mojom/scanner_feedback_ui.mojom",
  "ash/webui/scanning/mojom/scanning.mojom",
  "ash/webui/settings/public/constants/routes.mojom",
  "ash/webui/settings/public/constants/setting.mojom",
  "ash/webui/shimless_rma/mojom/shimless_rma.mojom",
  "ash/webui/shortcut_customization_ui/backend/search/search.mojom",
  "ash/webui/shortcut_customization_ui/mojom/shortcut_customization.mojom",
  "ash/webui/status_area_internals/mojom/status_area_internals.mojom",
  "cc/mojom/browser_controls_offset_tag_modifications.mojom"
]
def pathBlock1 : Array String := #[
  "cc/mojom/browser_controls_offset_tags.mojom",
  "cc/mojom/browser_controls_params.mojom",
  "cc/mojom/browser_controls_state.mojom",
  "cc/mojom/element_id.mojom",
  "cc/mojom/hit_test_opaqueness.mojom",
  "cc/mojom/layer_selection_bound.mojom",
  "cc/mojom/layer_tree_debug_state.mojom",
  "cc/mojom/layer_type.mojom",
  "cc/mojom/missing_tile_reason.mojom",
  "cc/mojom/overscroll_behavior.mojom",
  "cc/mojom/paint_flags.mojom",
  "cc/mojom/render_frame_metadata.mojom",
  "cc/mojom/render_surface_reason.mojom",
  "cc/mojom/root_scroll_offset_update_frequency.mojom",
  "cc/mojom/scrollbar_animator.mojom",
  "cc/mojom/synced_scroll_offset.mojom",
  "cc/mojom/touch_action.mojom",
  "cc/mojom/ui_resource_id.mojom",
  "chrome/browser/accessibility/page_colors.mojom",
  "chrome/browser/actor/ui/actor_overlay.mojom",
  "chrome/browser/ash/borealis/borealis_types.mojom",
  "chrome/browser/ash/crostini/crostini_types.mojom",
  "chrome/browser/browser_actuator/internals/browser_actuator_internals.mojom",
  "chrome/browser/contextual_cueing/internals/contextual_cueing_internals.mojom",
  "chrome/browser/contextual_tasks/contextual_tasks.mojom",
  "chrome/browser/contextual_tasks/contextual_tasks_internals.mojom",
  "chrome/browser/contextual_tasks/contextual_tasks_toolbar.mojom",
  "chrome/browser/contextual_tasks/contextual_tasks_types.mojom",
  "chrome/browser/glic/experimental_opt_in/glic_experimental_opt_in.mojom",
  "chrome/browser/glic/gemini_enterprise/gemini_enterprise.mojom",
  "chrome/browser/glic/host/glic.mojom",
  "chrome/browser/glic/host/glic_features.mojom",
  "chrome/browser/glic/host/glic_internals.mojom",
  "chrome/browser/glic/host/glic_overlay.mojom",
  "chrome/browser/glic/host/glic_webui.mojom",
  "chrome/browser/glic/selection/explain_fulfillment.mojom",
  "chrome/browser/glic/selection/selection_overlay.mojom",
  "chrome/browser/lens/core/mojom/geometry.mojom",
  "chrome/browser/lens/core/mojom/lens.mojom",
  "chrome/browser/lens/core/mojom/lens_ghost_loader.mojom",
  "chrome/browser/lens/core/mojom/lens_side_panel.mojom",
  "chrome/browser/lens/core/mojom/overlay_object.mojom",
  "chrome/browser/lens/core/mojom/page_content_type.mojom",
  "chrome/browser/lens/core/mojom/polygon.mojom",
  "chrome/browser/lens/core/mojom/text.mojom",
  "chrome/browser/lens/core/mojom/translate.mojom",
  "chrome/browser/media/media_engagement_score_details.mojom",
  "chrome/browser/new_tab_page/modules/file_suggestion/drive_suggestion.mojom",
  "chrome/browser/new_tab_page/modules/file_suggestion/file_suggestion.mojom",
  "chrome/browser/new_tab_page/modules/file_suggestion/microsoft_files.mojom",
  "chrome/browser/new_tab_page/modules/v2/calendar/calendar_data.mojom",
  "chrome/browser/new_tab_page/modules/v2/calendar/google_calendar.mojom",
  "chrome/browser/new_tab_page/modules/v2/calendar/outlook_calendar.mojom",
  "chrome/browser/new_tab_page/modules/v2/most_relevant_tab_resumption/most_relevant_tab_resumption.mojom",
  "chrome/browser/new_tab_page/modules/v2/most_relevant_tab_resumption/url_visit_types.mojom",
  "chrome/browser/new_tab_page/modules/v2/tab_groups/tab_groups.mojom",
  "chrome/browser/pwc/pwc.mojom",
  "chrome/browser/resource_coordinator/lifecycle_unit_state.mojom",
  "chrome/browser/resources/certificate_manager/certificate_manager.mojom",
  "chrome/browser/selection/mojom/action.mojom",
  "chrome/browser/ttc/core/eval_harness.mojom",
  "chrome/browser/ui/views/drive_picker_host/drive_picker_result_handler.mojom",
  "chrome/browser/ui/webui/access_code_cast/access_code_cast.mojom",
  "chrome/browser/ui/webui/ai_overlay_dialog/ai_overlay_dialog.mojom"
]
def pathBlock2 : Array String := #[
  "chrome/browser/ui/webui/ai_overlay_dialog/tools/tools.mojom",
  "chrome/browser/ui/webui/app_home/app_home.mojom",
  "chrome/browser/ui/webui/app_service_internals/app_service_internals.mojom",
  "chrome/browser/ui/webui/ash/add_supervision/add_supervision.mojom",
  "chrome/browser/ui/webui/ash/app_install/app_install.mojom",
  "chrome/browser/ui/webui/ash/cloud_upload/cloud_upload.mojom",
  "chrome/browser/ui/webui/ash/crostini_installer/crostini_installer.mojom",
  "chrome/browser/ui/webui/ash/dlp_internals/dlp_internals.mojom",
  "chrome/browser/ui/webui/ash/emoji/emoji_picker.mojom",
  "chrome/browser/ui/webui/ash/emoji/new_window_proxy.mojom",
  "chrome/browser/ui/webui/ash/enterprise_reporting/enterprise_reporting.mojom",
  "chrome/browser/ui/webui/ash/extended_updates/extended_updates.mojom",
  "chrome/browser/ui/webui/ash/launcher_internals/launcher_internals.mojom",
  "chrome/browser/ui/webui/ash/lobster/lobster.mojom",
  "chrome/browser/ui/webui/ash/login/mojom/screens_common.mojom",
  "chrome/browser/ui/webui/ash/login/mojom/screens_factory.mojom",
  "chrome/browser/ui/webui/ash/login/mojom/screens_login.mojom",
  "chrome/browser/ui/webui/ash/login/mojom/screens_oobe.mojom",
  "chrome/browser/ui/webui/ash/login/mojom/screens_osauth.mojom",
  "chrome/browser/ui/webui/ash/office_fallback/office_fallback.mojom",
  "chrome/browser/ui/webui/ash/parent_access/parent_access_ui.mojom",
  "chrome/browser/ui/webui/ash/sensor_info/sensor.mojom",
  "chrome/browser/ui/webui/ash/settings/pages/apps/mojom/app_notification_handler.mojom",
  "chrome/browser/ui/webui/ash/settings/pages/apps/mojom/app_parental_controls_handler.mojom",
  "chrome/browser/ui/webui/ash/settings/pages/date_time/mojom/date_time_handler.mojom",
  "chrome/browser/ui/webui/ash/settings/pages/device/display_settings/display_settings_provider.mojom",
  "chrome/browser/ui/webui/ash/settings/pages/device/input_device_settings/input_device_settings_provider.mojom",
  "chrome/browser/ui/webui/ash/settings/pages/files/mojom/google_drive_handler.mojom",
  "chrome/browser/ui/webui/ash/settings/pages/files/mojom/one_drive_handler.mojom",
  "chrome/browser/ui/webui/ash/settings/pages/people/mojom/graduation_handler.mojom",
  "chrome/browser/ui/webui/ash/settings/pages/privacy/mojom/app_permission_handler.mojom",
  "chrome/browser/ui/webui/ash/settings/pages/search/mojom/magic_boost_handler.mojom",
  "chrome/browser/ui/webui/ash/settings/search/mojom/search.mojom",
  "chrome/browser/ui/webui/ash/settings/search/mojom/search_result_icon.mojom",
  "chrome/browser/ui/webui/ash/settings/search/mojom/user_action_recorder.mojom",
  "chrome/browser/ui/webui/ash/skyvault/local_files_migration.mojom",
  "chrome/browser/ui/webui/bluetooth_internals/bluetooth_internals.mojom",
  "chrome/browser/ui/webui/chrome_finds_internals/chrome_finds_internals.mojom",
  "chrome/browser/ui/webui/content_settings/content_settings_internals.mojom",
  "chrome/browser/ui/webui/context_hub/context_hub.mojom",
  "chrome/browser/ui/webui/critical_actions/critical_actions.mojom",
  "chrome/browser/ui/webui/customize_buttons/customize_buttons.mojom",
  "chrome/browser/ui/webui/data_sharing/data_sharing.mojom",
  "chrome/browser/ui/webui/default_browser/default_browser_modal.mojom",
  "chrome/browser/ui/webui/default_browser/visual_guided_setter.mojom",
  "chrome/browser/ui/webui/discards/discards.mojom",
  "chrome/browser/ui/webui/discards/site_data.mojom",
  "chrome/browser/ui/webui/downloads/downloads.mojom",
  "chrome/browser/ui/webui/drive_picker_host/drive_picker_host.mojom",
  "chrome/browser/ui/webui/drive_picker_host/untrusted/drive_picker_host_untrusted.mojom",
  "chrome/browser/ui/webui/extensions_zero_state_promo/zero_state_promo.mojom",
  "chrome/browser/ui/webui/feature_showcase/default_browser.mojom",
  "chrome/browser/ui/webui/feature_showcase/feature_showcase.mojom",
  "chrome/browser/ui/webui/feature_showcase/gemini.mojom",
  "chrome/browser/ui/webui/feature_showcase/google_lens.mojom",
  "chrome/browser/ui/webui/feature_showcase/password_manager.mojom",
  "chrome/browser/ui/webui/feature_showcase/themes_and_customization.mojom",
  "chrome/browser/ui/webui/feed_internals/feed_internals.mojom",
  "chrome/browser/ui/webui/feedback/report_unsafe_site/report_unsafe_site.mojom",
  "chrome/browser/ui/webui/indigo_internals/indigo_internals.mojom",
  "chrome/browser/ui/webui/infobar_internals/infobar_internals.mojom",
  "chrome/browser/ui/webui/intro/finish_or_continue.mojom",
  "chrome/browser/ui/webui/intro/intro.mojom",
  "chrome/browser/ui/webui/intro/sign_in_celebration.mojom"
]
def pathBlock3 : Array String := #[
  "chrome/browser/ui/webui/intro/sign_in_promo.mojom",
  "chrome/browser/ui/webui/intro/welcome.mojom",
  "chrome/browser/ui/webui/iwa_dev/iwa_dev.mojom",
  "chrome/browser/ui/webui/location_internals/location_internals.mojom",
  "chrome/browser/ui/webui/multistep_filter_internals/multistep_filter_internals.mojom",
  "chrome/browser/ui/webui/nearby_share/nearby_share.mojom",
  "chrome/browser/ui/webui/nearby_share/nearby_share_share_type.mojom",
  "chrome/browser/ui/webui/new_tab_footer/new_tab_footer.mojom",
  "chrome/browser/ui/webui/new_tab_page/action_chips/action_chips.mojom",
  "chrome/browser/ui/webui/new_tab_page/foo/foo.mojom",
  "chrome/browser/ui/webui/new_tab_page/new_tab_page.mojom",
  "chrome/browser/ui/webui/new_tab_page/ntp_promo/ntp_promo.mojom",
  "chrome/browser/ui/webui/new_tab_page_third_party/new_tab_page_third_party.mojom",
  "chrome/browser/ui/webui/notifications_internals/notifications_internals.mojom",
  "chrome/browser/ui/webui/ntp_microsoft_auth/ntp_microsoft_auth_shared_ui.mojom",
  "chrome/browser/ui/webui/ntp_microsoft_auth/ntp_microsoft_auth_untrusted_ui.mojom",
  "chrome/browser/ui/webui/omnibox_everywhere/debug/omnibox_everywhere_debug.mojom",
  "chrome/browser/ui/webui/omnibox_everywhere/mojom/omnibox_everywhere.mojom",
  "chrome/browser/ui/webui/omnibox_internals/aim_eligibility/aim_eligibility.mojom",
  "chrome/browser/ui/webui/omnibox_internals/logging/logs.mojom",
  "chrome/browser/ui/webui/omnibox_internals/omnibox_internals.mojom",
  "chrome/browser/ui/webui/omnibox_popup/mojom/omnibox_popup.mojom",
  "chrome/browser/ui/webui/omnibox_popup/mojom/omnibox_popup_aim.mojom",
  "chrome/browser/ui/webui/on_device_internals/on_device_internals_page.mojom",
  "chrome/browser/ui/webui/on_device_translation_internals/on_device_translation_internals.mojom",
  "chrome/browser/ui/webui/organizer_panel/foreign_tabs.mojom",
  "chrome/browser/ui/webui/organizer_panel/organizer_panel.mojom",
  "chrome/browser/ui/webui/organizer_panel/tab_groups.mojom",
  "chrome/browser/ui/webui/page_action_internals/page_action_internals.mojom",
  "chrome/browser/ui/webui/password_manager/password_manager.mojom",
  "chrome/browser/ui/webui/reset_password/reset_password.mojom",
  "chrome/browser/ui/webui/search_engine_choice/search_engine_choice.mojom",
  "chrome/browser/ui/webui/segmentation_internals/segmentation_internals.mojom",
  "chrome/browser/ui/webui/settings/search/mojom/setting_id.mojom",
  "chrome/browser/ui/webui/settings/search/mojom/settings_search.mojom",
  "chrome/browser/ui/webui/side_panel/bookmarks/bookmarks.mojom",
  "chrome/browser/ui/webui/side_panel/comments/comments.mojom",
  "chrome/browser/ui/webui/side_panel/customize_chrome/customize_chrome.mojom",
  "chrome/browser/ui/webui/side_panel/customize_chrome/customize_toolbar/customize_toolbar.mojom",
  "chrome/browser/ui/webui/side_panel/customize_chrome/wallpaper_search/wallpaper_search.mojom",
  "chrome/browser/ui/webui/side_panel/reading_list/reading_list.mojom",
  "chrome/browser/ui/webui/signin/batch_upload/batch_upload.mojom",
  "chrome/browser/ui/webui/signin/cross_device_signin_qr_bubble/cross_device_signin_qr_bubble.mojom",
  "chrome/browser/ui/webui/signin/history_sync_optin/history_sync_optin.mojom",
  "chrome/browser/ui/webui/signin/signout_confirmation/signout_confirmation.mojom",
  "chrome/browser/ui/webui/skills/skills.mojom",
  "chrome/browser/ui/webui/subresource_filter/subresource_filter_internals.mojom",
  "chrome/browser/ui/webui/suggest_internals/suggest_internals.mojom",
  "chrome/browser/ui/webui/tab_search/tab_search.mojom",
  "chrome/browser/ui/webui/tab_strip_internals/tab_strip_internals.mojom",
  "chrome/browser/ui/webui/tabstrip_ntb/tabstrip_ntb.mojom",
  "chrome/browser/ui/webui/unexportable_keys_internals/unexportable_keys_internals.mojom",
  "chrome/browser/ui/webui/updater/updater_ui.mojom",
  "chrome/browser/ui/webui/usb_internals/usb_internals.mojom",
  "chrome/browser/ui/webui/user_education_internals/user_education_internals.mojom",
  "chrome/browser/ui/webui/watermark/watermark.mojom",
  "chrome/browser/ui/webui/web_app_internals/web_app_internals.mojom",
  "chrome/browser/ui/webui/webnn_internals/webnn_internals.mojom",
  "chrome/browser/ui/webui/whats_new/whats_new.mojom",
  "chrome/browser/ui/webui_browser/bookmark_bar.mojom",
  "chrome/browser/ui/webui_browser/browser.mojom",
  "chrome/browser/web_applications/mojom/user_display_mode.mojom",
  "chrome/browser/web_applications/mojom/web_app_shortcut_copier.mojom",
  "chrome/common/actor.mojom"
]
def pathBlock4 : Array String := #[
  "chrome/common/actor_webui.mojom",
  "chrome/common/chrome_render_frame.mojom",
  "chrome/common/compose/compose.mojom",
  "chrome/common/conflicts/module_event_sink_win.mojom",
  "chrome/common/font_prewarmer.mojom",
  "chrome/common/glic_enums.mojom",
  "chrome/common/google_accounts_private_api_extension.mojom",
  "chrome/common/importer/profile_import.mojom",
  "chrome/common/indigo/indigo.mojom",
  "chrome/common/mac/app_shim.mojom",
  "chrome/common/media/webrtc_logging.mojom",
  "chrome/common/mhtml_page_notifier.mojom",
  "chrome/common/net/net_error_page_support.mojom",
  "chrome/common/net_benchmarking.mojom",
  "chrome/common/network_diagnostics.mojom",
  "chrome/common/network_easter_egg.mojom",
  "chrome/common/offline_page_auto_fetcher.mojom",
  "chrome/common/open_search_description_document_handler.mojom",
  "chrome/common/password_manager/remote_actor_credential_sharing.mojom",
  "chrome/common/plugin.mojom",
  "chrome/common/read_anything/distillation_evaluator.mojom",
  "chrome/common/read_anything/read_anything.mojom",
  "chrome/common/readaloud/read_aloud.mojom",
  "chrome/common/renderer_configuration.mojom",
  "chrome/common/request_header_integrity/chrome_companero.mojom",
  "chrome/common/request_header_integrity/platform_runtime.mojom",
  "chrome/common/sandbox_status_extension_android.mojom",
  "chrome/common/search/search.mojom",
  "chrome/common/supervised_user_commands.mojom",
  "chrome/common/tab_context_decryption_token_extension.mojom",
  "chrome/common/trusted_vault_encryption_keys_extension.mojom",
  "chrome/common/wallet/boarding_pass_extractor.mojom",
  "chrome/credential_provider/gaiacp/mojom/gaia_credential_provider_win_hid.mojom",
  "chrome/enterprise_companion/mojom/enterprise_companion.mojom",
  "chrome/enterprise_companion/mojom/policy_fetch_reason.mojom",
  "chrome/services/file_util/public/mojom/constants.mojom",
  "chrome/services/file_util/public/mojom/document_analysis_service.mojom",
  "chrome/services/file_util/public/mojom/file_util_service.mojom",
  "chrome/services/file_util/public/mojom/safe_archive_analyzer.mojom",
  "chrome/services/file_util/public/mojom/single_file_extractor.mojom",
  "chrome/services/file_util/public/mojom/zip_file_creator.mojom",
  "chrome/services/mac_notifications/public/mojom/mac_notifications.mojom",
  "chrome/services/pdf/public/mojom/pdf_progressive_searchifier.mojom",
  "chrome/services/pdf/public/mojom/pdf_searchifier.mojom",
  "chrome/services/pdf/public/mojom/pdf_service.mojom",
  "chrome/services/pdf/public/mojom/pdf_thumbnailer.mojom",
  "chrome/services/printing/public/mojom/pdf_flattener.mojom",
  "chrome/services/printing/public/mojom/pdf_nup_converter.mojom",
  "chrome/services/printing/public/mojom/pdf_render_settings.mojom",
  "chrome/services/printing/public/mojom/pdf_to_emf_converter.mojom",
  "chrome/services/printing/public/mojom/pdf_to_pwg_raster_converter.mojom",
  "chrome/services/printing/public/mojom/print_backend_service.mojom",
  "chrome/services/printing/public/mojom/printing_service.mojom",
  "chrome/services/redirection/public/mojom/redirection_service.mojom",
  "chrome/services/removable_storage_writer/public/mojom/removable_storage_writer.mojom",
  "chrome/services/util_win/public/mojom/uia_element_probe.mojom",
  "chrome/services/util_win/public/mojom/util_read_icon.mojom",
  "chrome/services/util_win/public/mojom/util_win.mojom",
  "chrome/test/data/webui/chromeos/web_ui_test.mojom",
  "chrome/test/data/webui/mojo/foobar.mojom",
  "chrome/test/data/webui/mojo/mojo_file_system_access_test.mojom",
  "chrome/updater/mojom/updater_service.mojom",
  "chrome/updater/mojom/updater_service_internal.mojom",
  "chrome/updater/net/mac/mojom/updater_fetcher.mojom"
]
def pathBlock5 : Array String := #[
  "chromecast/bindings/public/mojom/api_bindings.mojom",
  "chromecast/browser/mojom/cast_content_window.mojom",
  "chromecast/browser/mojom/cast_web_contents.mojom",
  "chromecast/browser/mojom/cast_web_service.mojom",
  "chromecast/browser/webui/mojom/webui.mojom",
  "chromecast/common/mojom/activity_window.mojom",
  "chromecast/common/mojom/application_media_capabilities.mojom",
  "chromecast/common/mojom/audio_socket.mojom",
  "chromecast/common/mojom/cast_demo.mojom",
  "chromecast/common/mojom/constants.mojom",
  "chromecast/common/mojom/feature_manager.mojom",
  "chromecast/common/mojom/gesture.mojom",
  "chromecast/common/mojom/js_channel.mojom",
  "chromecast/common/mojom/media_caps.mojom",
  "chromecast/common/mojom/metrics_helper.mojom",
  "chromecast/common/mojom/queryable_data_store.mojom",
  "chromecast/common/mojom/service_connector.mojom",
  "chromecast/common/mojom/settings_ui.mojom",
  "chromecast/media/mojom/media_types.mojom",
  "chromecast/media/service/mojom/video_geometry_setter.mojom",
  "chromecast/mojo/mojom/remote_interfaces.mojom",
  "chromecast/ui/mojom/display_settings.mojom",
  "chromecast/ui/mojom/ui_service.mojom",
  "chromeos/ash/components/audio/public/mojom/cros_audio_config.mojom",
  "chromeos/ash/components/drivefs/mojom/drivefs.mojom",
  "chromeos/ash/components/drivefs/mojom/drivefs_native_messaging.mojom",
  "chromeos/ash/components/drivefs/mojom/fake_drivefs_launcher.mojom",
  "chromeos/ash/components/drivefs/mojom/notifications.mojom",
  "chromeos/ash/components/drivefs/mojom/pinning_manager_types.mojom",
  "chromeos/ash/components/emoji/emoji_search.mojom",
  "chromeos/ash/components/emoji/tenor_types.mojom",
  "chromeos/ash/components/enhanced_network_tts/mojom/enhanced_network_tts.mojom",
  "chromeos/ash/components/language_packs/public/mojom/language_packs.mojom",
  "chromeos/ash/components/local_search_service/public/mojom/index.mojom",
  "chromeos/ash/components/local_search_service/public/mojom/local_search_service.mojom",
  "chromeos/ash/components/local_search_service/public/mojom/types.mojom",
  "chromeos/ash/components/mantis/mojom/mantis_processor.mojom",
  "chromeos/ash/components/mantis/mojom/mantis_service.mojom",
  "chromeos/ash/components/mojo_service_manager/mojom/mojo_service_manager.mojom",
  "chromeos/ash/components/multidevice/mojom/multidevice_types.mojom",
  "chromeos/ash/components/proximity_auth/public/mojom/auth_type.mojom",
  "chromeos/ash/components/smbfs/mojom/file_path.mojom",
  "chromeos/ash/components/smbfs/mojom/ip_address.mojom",
  "chromeos/ash/components/smbfs/mojom/smbfs.mojom",
  "chromeos/ash/components/trash_service/public/mojom/trash_service.mojom",
  "chromeos/ash/experiences/arc/mojom/adbd.mojom",
  "chromeos/ash/experiences/arc/mojom/anr.mojom",
  "chromeos/ash/experiences/arc/mojom/app.mojom",
  "chromeos/ash/experiences/arc/mojom/app_permissions.mojom",
  "chromeos/ash/experiences/arc/mojom/appfuse.mojom",
  "chromeos/ash/experiences/arc/mojom/arc_bridge.mojom",
  "chromeos/ash/experiences/arc/mojom/arc_wifi.mojom",
  "chromeos/ash/experiences/arc/mojom/audio.mojom",
  "chromeos/ash/experiences/arc/mojom/auth.mojom",
  "chromeos/ash/experiences/arc/mojom/backup_settings.mojom",
  "chromeos/ash/experiences/arc/mojom/bitmap.mojom",
  "chromeos/ash/experiences/arc/mojom/bluetooth.mojom",
  "chromeos/ash/experiences/arc/mojom/boot_phase_monitor.mojom",
  "chromeos/ash/experiences/arc/mojom/camera.mojom",
  "chromeos/ash/experiences/arc/mojom/camera_intent.mojom",
  "chromeos/ash/experiences/arc/mojom/chrome_feature_flags.mojom",
  "chromeos/ash/experiences/arc/mojom/compatibility_mode.mojom",
  "chromeos/ash/experiences/arc/mojom/crash_collector.mojom",
  "chromeos/ash/experiences/arc/mojom/crosh.mojom"
]
def pathBlock6 : Array String := #[
  "chromeos/ash/experiences/arc/mojom/digital_goods.mojom",
  "chromeos/ash/experiences/arc/mojom/disk_space.mojom",
  "chromeos/ash/experiences/arc/mojom/enterprise_reporting.mojom",
  "chromeos/ash/experiences/arc/mojom/error_notification.mojom",
  "chromeos/ash/experiences/arc/mojom/file_system.mojom",
  "chromeos/ash/experiences/arc/mojom/gfx.mojom",
  "chromeos/ash/experiences/arc/mojom/iio_sensor.mojom",
  "chromeos/ash/experiences/arc/mojom/ime.mojom",
  "chromeos/ash/experiences/arc/mojom/input_method_manager.mojom",
  "chromeos/ash/experiences/arc/mojom/intent_common.mojom",
  "chromeos/ash/experiences/arc/mojom/intent_helper.mojom",
  "chromeos/ash/experiences/arc/mojom/keymaster.mojom",
  "chromeos/ash/experiences/arc/mojom/keymint.mojom",
  "chromeos/ash/experiences/arc/mojom/kiosk.mojom",
  "chromeos/ash/experiences/arc/mojom/media_session.mojom",
  "chromeos/ash/experiences/arc/mojom/memory.mojom",
  "chromeos/ash/experiences/arc/mojom/metrics.mojom",
  "chromeos/ash/experiences/arc/mojom/midis.mojom",
  "chromeos/ash/experiences/arc/mojom/nearby_share.mojom",
  "chromeos/ash/experiences/arc/mojom/net.mojom",
  "chromeos/ash/experiences/arc/mojom/net_shared.mojom",
  "chromeos/ash/experiences/arc/mojom/notifications.mojom",
  "chromeos/ash/experiences/arc/mojom/obb_mounter.mojom",
  "chromeos/ash/experiences/arc/mojom/oemcrypto.mojom",
  "chromeos/ash/experiences/arc/mojom/on_device_safety.mojom",
  "chromeos/ash/experiences/arc/mojom/pip.mojom",
  "chromeos/ash/experiences/arc/mojom/policy.mojom",
  "chromeos/ash/experiences/arc/mojom/power.mojom",
  "chromeos/ash/experiences/arc/mojom/print_common.mojom",
  "chromeos/ash/experiences/arc/mojom/print_spooler.mojom",
  "chromeos/ash/experiences/arc/mojom/privacy_items.mojom",
  "chromeos/ash/experiences/arc/mojom/process.mojom",
  "chromeos/ash/experiences/arc/mojom/protected_buffer_manager.mojom",
  "chromeos/ash/experiences/arc/mojom/scale_factor.mojom",
  "chromeos/ash/experiences/arc/mojom/screen_capture.mojom",
  "chromeos/ash/experiences/arc/mojom/sharesheet.mojom",
  "chromeos/ash/experiences/arc/mojom/system_state.mojom",
  "chromeos/ash/experiences/arc/mojom/system_ui.mojom",
  "chromeos/ash/experiences/arc/mojom/tracing.mojom",
  "chromeos/ash/experiences/arc/mojom/tts.mojom",
  "chromeos/ash/experiences/arc/mojom/video.mojom",
  "chromeos/ash/experiences/arc/mojom/video_common.mojom",
  "chromeos/ash/experiences/arc/mojom/video_decode_accelerator.mojom",
  "chromeos/ash/experiences/arc/mojom/video_decoder.mojom",
  "chromeos/ash/experiences/arc/mojom/video_encode_accelerator.mojom",
  "chromeos/ash/experiences/arc/mojom/video_frame_pool.mojom",
  "chromeos/ash/experiences/arc/mojom/video_protected_buffer_allocator.mojom",
  "chromeos/ash/experiences/arc/mojom/volume_mounter.mojom",
  "chromeos/ash/experiences/arc/mojom/wake_lock.mojom",
  "chromeos/ash/experiences/arc/mojom/wallpaper.mojom",
  "chromeos/ash/experiences/arc/mojom/webapk.mojom",
  "chromeos/ash/services/auth_factor_config/public/mojom/auth_factor_config.mojom",
  "chromeos/ash/services/bluetooth_config/public/mojom/cros_bluetooth_config.mojom",
  "chromeos/ash/services/boca/babelorca/mojom/tachyon_parsing_service.mojom",
  "chromeos/ash/services/cellular_setup/public/mojom/cellular_setup.mojom",
  "chromeos/ash/services/cellular_setup/public/mojom/esim_manager.mojom",
  "chromeos/ash/services/connectivity/public/mojom/passpoint.mojom",
  "chromeos/ash/services/coral/public/mojom/coral_service.mojom",
  "chromeos/ash/services/cros_healthd/private/mojom/cros_healthd_internal.mojom",
  "chromeos/ash/services/cros_healthd/public/mojom/cros_healthd.mojom",
  "chromeos/ash/services/cros_healthd/public/mojom/cros_healthd_diagnostics.mojom",
  "chromeos/ash/services/cros_healthd/public/mojom/cros_healthd_event_reporters.mojom",
  "chromeos/ash/services/cros_healthd/public/mojom/cros_healthd_events.mojom",
  "chromeos/ash/services/cros_healthd/public/mojom/cros_healthd_exception.mojom"
]
def pathBlock7 : Array String := #[
  "chromeos/ash/services/cros_healthd/public/mojom/cros_healthd_probe.mojom",
  "chromeos/ash/services/cros_healthd/public/mojom/cros_healthd_routines.mojom",
  "chromeos/ash/services/cros_healthd/public/mojom/nullable_primitives.mojom",
  "chromeos/ash/services/cros_healthd/testing/bindings/mojom/state.mojom",
  "chromeos/ash/services/cros_safety/public/mojom/cros_safety.mojom",
  "chromeos/ash/services/cros_safety/public/mojom/cros_safety_service.mojom",
  "chromeos/ash/services/device_sync/public/mojom/device_sync.mojom",
  "chromeos/ash/services/heartd/public/mojom/heartd.mojom",
  "chromeos/ash/services/hotspot_config/public/mojom/cros_hotspot_config.mojom",
  "chromeos/ash/services/ime/public/mojom/connection_factory.mojom",
  "chromeos/ash/services/ime/public/mojom/ime_service.mojom",
  "chromeos/ash/services/ime/public/mojom/input_engine.mojom",
  "chromeos/ash/services/ime/public/mojom/input_method.mojom",
  "chromeos/ash/services/ime/public/mojom/input_method_host.mojom",
  "chromeos/ash/services/ime/public/mojom/input_method_user_data.mojom",
  "chromeos/ash/services/ime/public/mojom/japanese_settings.mojom",
  "chromeos/ash/services/ime/public/mojom/user_data_japanese_dictionary.mojom",
  "chromeos/ash/services/keymanagement/public/mojom/cert_store_types.mojom",
  "chromeos/ash/services/keymaster/public/mojom/cert_store.mojom",
  "chromeos/ash/services/keymint/public/mojom/cert_store.mojom",
  "chromeos/ash/services/multidevice_setup/public/mojom/multidevice_setup.mojom",
  "chromeos/ash/services/nearby/public/mojom/firewall_hole.mojom",
  "chromeos/ash/services/nearby/public/mojom/mdns.mojom",
  "chromeos/ash/services/nearby/public/mojom/nearby_connections.mojom",
  "chromeos/ash/services/nearby/public/mojom/nearby_connections_types.mojom",
  "chromeos/ash/services/nearby/public/mojom/nearby_decoder.mojom",
  "chromeos/ash/services/nearby/public/mojom/nearby_decoder_types.mojom",
  "chromeos/ash/services/nearby/public/mojom/nearby_share_settings.mojom",
  "chromeos/ash/services/nearby/public/mojom/nearby_share_target_types.mojom",
  "chromeos/ash/services/nearby/public/mojom/quick_start_decoder.mojom",
  "chromeos/ash/services/nearby/public/mojom/quick_start_decoder_types.mojom",
  "chromeos/ash/services/nearby/public/mojom/sharing.mojom",
  "chromeos/ash/services/nearby/public/mojom/tcp_server_socket_port.mojom",
  "chromeos/ash/services/nearby/public/mojom/tcp_socket_factory.mojom",
  "chromeos/ash/services/nearby/public/mojom/webrtc.mojom",
  "chromeos/ash/services/nearby/public/mojom/webrtc_signaling_messenger.mojom",
  "chromeos/ash/services/orca/public/mojom/orca_service.mojom",
  "chromeos/ash/services/quick_pair/public/mojom/fast_pair_data_parser.mojom",
  "chromeos/ash/services/quick_pair/public/mojom/quick_pair_service.mojom",
  "chromeos/ash/services/recording/public/mojom/recording_service.mojom",
  "chromeos/ash/services/rollback_network_config/public/mojom/rollback_network_config.mojom",
  "chromeos/ash/services/secure_channel/public/mojom/nearby_connector.mojom",
  "chromeos/ash/services/secure_channel/public/mojom/secure_channel.mojom",
  "chromeos/ash/services/secure_channel/public/mojom/secure_channel_types.mojom",
  "chromeos/ash/services/wifi_direct/public/mojom/wifi_direct_manager.mojom",
  "chromeos/components/cdm_factory_daemon/mojom/browser_cdm_factory.mojom",
  "chromeos/components/cdm_factory_daemon/mojom/cdm_factory_daemon.mojom",
  "chromeos/components/cdm_factory_daemon/mojom/cdm_storage.mojom",
  "chromeos/components/cdm_factory_daemon/mojom/content_decryption_module.mojom",
  "chromeos/components/cdm_factory_daemon/mojom/output_protection.mojom",
  "chromeos/components/in_session_auth/mojom/in_session_auth.mojom",
  "chromeos/components/mahi/public/mojom/content_extraction.mojom",
  "chromeos/components/payments/mojom/payment_app.mojom",
  "chromeos/components/payments/mojom/payment_app_types.mojom",
  "chromeos/components/print_management/mojom/printing_manager.mojom",
  "chromeos/components/quick_answers/public/mojom/spell_check.mojom",
  "chromeos/components/remote_apps/mojom/remote_apps.mojom",
  "chromeos/components/sensors/mojom/cros_sensor_service.mojom",
  "chromeos/components/sensors/mojom/sensor.mojom",
  "chromeos/services/chromebox_for_meetings/public/mojom/cfm_browser.mojom",
  "chromeos/services/chromebox_for_meetings/public/mojom/cfm_service_manager.mojom",
  "chromeos/services/chromebox_for_meetings/public/mojom/external_display_brightness.mojom",
  "chromeos/services/chromebox_for_meetings/public/mojom/meet_browser.mojom",
  "chromeos/services/chromebox_for_meetings/public/mojom/meet_devices_data_aggregator.mojom"
]
def pathBlock8 : Array String := #[
  "chromeos/services/chromebox_for_meetings/public/mojom/meet_devices_diagnostics.mojom",
  "chromeos/services/chromebox_for_meetings/public/mojom/meet_devices_hotrod_status.mojom",
  "chromeos/services/chromebox_for_meetings/public/mojom/meet_devices_info.mojom",
  "chromeos/services/chromebox_for_meetings/public/mojom/meet_devices_logger.mojom",
  "chromeos/services/chromebox_for_meetings/public/mojom/xu_camera.mojom",
  "chromeos/services/machine_learning/public/mojom/document_scanner.mojom",
  "chromeos/services/machine_learning/public/mojom/document_scanner_param_types.mojom",
  "chromeos/services/machine_learning/public/mojom/grammar_checker.mojom",
  "chromeos/services/machine_learning/public/mojom/graph_executor.mojom",
  "chromeos/services/machine_learning/public/mojom/handwriting_recognizer.mojom",
  "chromeos/services/machine_learning/public/mojom/heatmap_palm_rejection.mojom",
  "chromeos/services/machine_learning/public/mojom/image_content_annotation.mojom",
  "chromeos/services/machine_learning/public/mojom/machine_learning_service.mojom",
  "chromeos/services/machine_learning/public/mojom/model.mojom",
  "chromeos/services/machine_learning/public/mojom/soda.mojom",
  "chromeos/services/machine_learning/public/mojom/tensor.mojom",
  "chromeos/services/machine_learning/public/mojom/text_classifier.mojom",
  "chromeos/services/machine_learning/public/mojom/text_suggester.mojom",
  "chromeos/services/machine_learning/public/mojom/web_platform_handwriting.mojom",
  "chromeos/services/media_perception/public/mojom/media_perception.mojom",
  "chromeos/services/media_perception/public/mojom/media_perception_service.mojom",
  "chromeos/services/network_config/public/mojom/constants.mojom",
  "chromeos/services/network_config/public/mojom/cros_network_config.mojom",
  "chromeos/services/network_config/public/mojom/network_types.mojom",
  "chromeos/services/network_health/public/mojom/network_diagnostics.mojom",
  "chromeos/services/network_health/public/mojom/network_health.mojom",
  "chromeos/services/network_health/public/mojom/network_health_types.mojom",
  "chromeos/services/tts/public/mojom/tts_service.mojom",
  "codelabs/cpp101/solutions/services/math/public/mojom/math_service.mojom",
  "codelabs/mojo_examples/mojom/interface.mojom",
  "components/account_id/mojom/account_id.mojom",
  "components/actor/public/mojom/actor_internals.mojom",
  "components/actor/public/mojom/actor_types.mojom",
  "components/autofill/content/common/mojom/autofill_agent.mojom",
  "components/autofill/content/common/mojom/autofill_driver.mojom",
  "components/autofill/core/browser/data_model/autofill_ai/autofill_ai_enums.mojom",
  "components/autofill/core/browser/data_model/payments/enum_types.mojom",
  "components/autofill/core/browser/ml_model/logging/autofill_ml_internals.mojom",
  "components/autofill/core/common/mojom/autofill_types.mojom",
  "components/autofill/core/common/mojom/test_autofill_types.mojom",
  "components/browser_apis/bookmarks/bookmarks_api.mojom",
  "components/browser_apis/browser_controls/browser_controls_api.mojom",
  "components/browser_apis/browser_controls/browser_controls_api_data_model.mojom",
  "components/browser_apis/tab_drag/tab_drag_api.mojom",
  "components/browser_apis/tab_strip/tab_strip_api.mojom",
  "components/browser_apis/tab_strip/tab_strip_api_data_model.mojom",
  "components/browser_apis/tab_strip/tab_strip_api_events.mojom",
  "components/browser_apis/tab_strip/tab_strip_api_types.mojom",
  "components/browser_apis/tab_strip/tab_strip_experiment_api.mojom",
  "components/browser_apis/tab_strip/tab_strip_ui_controller.mojom",
  "components/browser_apis/ui_controllers/bookmark_bar/bookmark_bar_api.mojom",
  "components/browser_apis/ui_controllers/toolbar/extensions_bar.mojom",
  "components/browser_apis/ui_controllers/toolbar/extensions_bar_data_model.mojom",
  "components/browser_apis/ui_controllers/toolbar/icon_handle.mojom",
  "components/browser_apis/ui_controllers/toolbar/toolbar_ui_api.mojom",
  "components/browser_apis/ui_controllers/toolbar/toolbar_ui_api_data_model.mojom",
  "components/cast_streaming/common/public/mojom/demuxer_connector.mojom",
  "components/cast_streaming/common/public/mojom/renderer_controller.mojom",
  "components/chromeos_camera/common/dmabuf.mojom",
  "components/chromeos_camera/common/jpeg_encode_accelerator.mojom",
  "components/chromeos_camera/common/mjpeg_decode_accelerator.mojom",
  "components/commerce/core/internals/mojom/commerce_internals.mojom",
  "components/commerce/core/mojom/commerce_web_extractor.mojom",
  "components/commerce/core/mojom/price_insights.mojom"
]
def pathBlock9 : Array String := #[
  "components/commerce/core/mojom/price_tracking.mojom",
  "components/commerce/core/mojom/shared.mojom",
  "components/commerce/core/mojom/shopping_service.mojom",
  "components/compose/core/browser/compose_enums.mojom",
  "components/content_capture/common/content_capture.mojom",
  "components/content_capture/common/content_capture_data.mojom",
  "components/content_settings/common/content_settings_agent.mojom",
  "components/content_settings/common/content_settings_manager.mojom",
  "components/content_settings/core/common/content_settings.mojom",
  "components/content_settings/core/common/content_settings_enums.mojom",
  "components/content_settings/core/common/content_settings_types.mojom",
  "components/continuous_search/common/public/mojom/continuous_search.mojom",
  "components/data_sharing/data_sharing_internals/webui/data_sharing_internals.mojom",
  "components/data_sharing/public/logger_common.mojom",
  "components/data_sharing/public/protocol/group_data.mojom",
  "components/device_signals/core/common/mojom/system_signals.mojom",
  "components/digital_goods/mojom/digital_goods.mojom",
  "components/discardable_memory/public/mojom/discardable_shared_memory_manager.mojom",
  "components/dom_distiller/content/common/mojom/distillability_service.mojom",
  "components/dom_distiller/content/common/mojom/distiller_javascript_service.mojom",
  "components/dom_distiller/core/mojom/distilled_page_prefs.mojom",
  "components/download/public/common/download_stream.mojom",
  "components/enterprise/connectors/connectors_internals.mojom",
  "components/enterprise/watermarking/mojom/watermark.mojom",
  "components/facilitated_payments/core/mojom/facilitated_payments_agent.mojom",
  "components/global_media_controls/public/mojom/device_service.mojom",
  "components/guest_contents/common/guest_contents.mojom",
  "components/guest_view/browser/slim_web_view/slim_web_view.mojom",
  "components/guest_view/common/guest_view.mojom",
  "components/heap_profiling/in_process/mojom/snapshot_controller.mojom",
  "components/heap_profiling/in_process/mojom/test_connector.mojom",
  "components/history_clusters/history_clusters_internals/webui/history_clusters_internals.mojom",
  "components/history_clusters/public/mojom/history_cluster_types.mojom",
  "components/input/render_input_router.mojom",
  "components/js_injection/common/enum.mojom",
  "components/js_injection/common/interfaces.mojom",
  "components/language_detection/content/common/language_detection.mojom",
  "components/lens/lens_metadata.mojom",
  "components/media_control/mojom/media_playback_options.mojom",
  "components/media_gallery_util/public/mojom/media_parser.mojom",
  "components/media_router/common/mojom/debugger.mojom",
  "components/media_router/common/mojom/logger.mojom",
  "components/media_router/common/mojom/media_controller.mojom",
  "components/media_router/common/mojom/media_route_provider_id.mojom",
  "components/media_router/common/mojom/media_router.mojom",
  "components/media_router/common/mojom/media_router_traits_test_service.mojom",
  "components/media_router/common/mojom/media_status.mojom",
  "components/media_router/common/mojom/route_request_result_code.mojom",
  "components/metrics/dwa/mojom/dwa_interface.mojom",
  "components/metrics/private_metrics/mojom/private_metrics_interface.mojom",
  "components/metrics/public/mojom/call_stack_profile_collector.mojom",
  "components/metrics/public/mojom/call_stack_profile_collector_test.mojom",
  "components/metrics/public/mojom/histogram_fetcher.mojom",
  "components/metrics/public/mojom/profile_params.mojom",
  "components/metrics/public/mojom/single_sample_metrics.mojom",
  "components/metrics/structured/mojom/event.mojom",
  "components/mirroring/mojom/cast_message_channel.mojom",
  "components/mirroring/mojom/mirroring_service.mojom",
  "components/mirroring/mojom/resource_provider.mojom",
  "components/mirroring/mojom/session_observer.mojom",
  "components/mirroring/mojom/session_parameters.mojom",
  "components/network_hints/common/network_hints.mojom",
  "components/no_state_prefetch/common/no_state_prefetch_canceler.mojom",
  "components/no_state_prefetch/common/render_frame_prerender_messages.mojom"
]
def pathBlock10 : Array String := #[
  "components/notebooks/internals/webui/notebooks_internals.mojom",
  "components/ntp_tiles/tile_source.mojom",
  "components/ntp_tiles/tile_type.mojom",
  "components/omnibox/browser/fusebox_action.mojom",
  "components/omnibox/browser/omnibox.mojom",
  "components/omnibox/browser/searchbox.mojom",
  "components/omnibox/browser/suggest_template_info.mojom",
  "components/omnibox/composebox/composebox_query.mojom",
  "components/on_device_translation/public/mojom/on_device_translation_service.mojom",
  "components/on_device_translation/public/mojom/translator.mojom",
  "components/on_load_script_injector/on_load_script_injector.mojom",
  "components/optimization_guide/content/mojom/page_text_service.mojom",
  "components/optimization_guide/core/optimization_guide_common.mojom",
  "components/optimization_guide/optimization_guide_internals/webui/optimization_guide_internals.mojom",
  "components/optimization_guide/public/mojom/model_broker.mojom",
  "components/optimization_guide/public/mojom/model_broker_debug.mojom",
  "components/origin_matcher/origin_matcher.mojom",
  "components/os_crypt/async/common/algorithm.mojom",
  "components/os_crypt/async/common/encryptor.mojom",
  "components/page_content_annotations/content/mojom/page_stability.mojom",
  "components/page_image_service/mojom/page_image_service.mojom",
  "components/page_load_metrics/common/page_load_metrics.mojom",
  "components/paint_preview/common/mojom/paint_preview_recorder.mojom",
  "components/paint_preview/common/mojom/paint_preview_types.mojom",
  "components/password_manager/services/csv_password/public/mojom/csv_password_parser.mojom",
  "components/payments/mojom/payment_request_data.mojom",
  "components/performance_manager/public/mojom/coordination_unit.mojom",
  "components/performance_manager/public/mojom/lifecycle.mojom",
  "components/performance_manager/public/mojom/v8_contexts.mojom",
  "components/performance_manager/public/mojom/web_memory.mojom",
  "components/persistent_cache/mojom/persistent_cache.mojom",
  "components/policy/resources/webui/mojom/policy.mojom",
  "components/printing/common/print.mojom",
  "components/private_ai/mojom/oak_session.mojom",
  "components/private_ai/private_ai_internals/webui/private_ai_internals.mojom",
  "components/record_replay/core/common/record_replay.mojom",
  "components/remote_cocoa/common/alert.mojom",
  "components/remote_cocoa/common/application.mojom",
  "components/remote_cocoa/common/font.mojom",
  "components/remote_cocoa/common/menu.mojom",
  "components/remote_cocoa/common/native_widget_ns_window.mojom",
  "components/remote_cocoa/common/native_widget_ns_window_host.mojom",
  "components/remote_cocoa/common/select_file_dialog.mojom",
  "components/remote_cocoa/common/text_input_host.mojom",
  "components/safe_browsing/content/common/safe_browsing.mojom",
  "components/safe_browsing/core/common/safe_browsing_url_checker.mojom",
  "components/schema_org/common/improved_metadata.mojom",
  "components/schema_org/common/metadata.mojom",
  "components/security_interstitials/core/common/mojom/interstitial_commands.mojom",
  "components/services/filesystem/public/mojom/directory.mojom",
  "components/services/filesystem/public/mojom/types.mojom",
  "components/services/font/public/mojom/font_service.mojom",
  "components/services/font_data/public/mojom/font_data_service.mojom",
  "components/services/paint_preview_compositor/public/mojom/paint_preview_compositor.mojom",
  "components/services/patch/public/mojom/file_patcher.mojom",
  "components/services/print_compositor/public/mojom/print_compositor.mojom",
  "components/services/quarantine/public/mojom/quarantine.mojom",
  "components/services/storage/privileged/mojom/bucket_client_info.mojom",
  "components/services/storage/privileged/mojom/indexed_db_control.mojom",
  "components/services/storage/privileged/mojom/indexed_db_control_test.mojom",
  "components/services/storage/privileged/mojom/indexed_db_internals_types.mojom",
  "components/services/storage/public/mojom/blob_storage_context.mojom",
  "components/services/storage/public/mojom/buckets/bucket_id.mojom",
  "components/services/storage/public/mojom/buckets/bucket_info.mojom"
]
def pathBlock11 : Array String := #[
  "components/services/storage/public/mojom/buckets/bucket_locator.mojom",
  "components/services/storage/public/mojom/cache_storage_control.mojom",
  "components/services/storage/public/mojom/file_system_access_context.mojom",
  "components/services/storage/public/mojom/filesystem/directory.mojom",
  "components/services/storage/public/mojom/local_storage_control.mojom",
  "components/services/storage/public/mojom/quota_client.mojom",
  "components/services/storage/public/mojom/service_worker_database.mojom",
  "components/services/storage/public/mojom/service_worker_storage_control.mojom",
  "components/services/storage/public/mojom/session_storage_control.mojom",
  "components/services/storage/public/mojom/storage_policy_update.mojom",
  "components/services/storage/public/mojom/storage_service.mojom",
  "components/services/storage/public/mojom/storage_usage_info.mojom",
  "components/services/unzip/public/mojom/unzipper.mojom",
  "components/site_engagement/core/mojom/site_engagement_details.mojom",
  "components/skills/public/skill.mojom",
  "components/skills/public/skill_metrics.mojom",
  "components/spellcheck/common/spellcheck.mojom",
  "components/spellcheck/common/spellcheck_panel.mojom",
  "components/sqlite_vfs/mojom/sqlite_vfs.mojom",
  "components/subresource_filter/content/mojom/subresource_filter.mojom",
  "components/subresource_filter/core/mojom/subresource_filter.mojom",
  "components/surface_embed/common/surface_embed.mojom",
  "components/system_media_controls/mac/remote_cocoa/system_media_controls.mojom",
  "components/tab_groups/public/mojom/tab_group_types.mojom",
  "components/tabs/public/mojom/tabs.mojom",
  "components/translate/content/common/translate.mojom",
  "components/unexportable_keys/mojom/unexportable_key_service.mojom",
  "components/url_rewrite/mojom/url_request_rewrite.mojom",
  "components/user_data_importer/mojom/bookmark_html_parser.mojom",
  "components/user_education/webui/user_education.mojom",
  "components/variations/variations.mojom",
  "components/visitedlink/common/visitedlink.mojom",
  "components/viz/service/debugger/mojom/viz_debugger.mojom",
  "components/vrp_flags/vrp_flags.mojom",
  "components/wallet/content/common/mojom/image_extractor.mojom",
  "components/web_cache/public/mojom/web_cache.mojom",
  "components/web_package/mojom/web_bundle_parser.mojom",
  "components/webapps/common/web_page_metadata.mojom",
  "components/webapps/common/web_page_metadata_agent.mojom",
  "components/webui/chrome_urls/mojom/chrome_urls.mojom",
  "content/browser/indexed_db/indexed_db_internals.mojom",
  "content/browser/process_internals/process_internals.mojom",
  "content/browser/tracing/traces_internals/traces_internals.mojom",
  "content/browser/xr/webxr_internals/mojom/webxr_internals.mojom",
  "content/common/agent_scheduling_group.mojom",
  "content/common/associated_interfaces.mojom",
  "content/common/child_process.mojom",
  "content/common/dom_automation_controller.mojom",
  "content/common/download/mhtml_file_writer.mojom",
  "content/common/field_trial_recorder.mojom",
  "content/common/frame.mojom",
  "content/common/frame_messages.mojom",
  "content/common/gin_java_bridge.mojom",
  "content/common/input/input_injector.mojom",
  "content/common/media/media_log_records.mojom",
  "content/common/memory_coordinator/mojom/memory_consumer_traits_test.mojom",
  "content/common/memory_coordinator/mojom/memory_coordinator.mojom",
  "content/common/memory_coordinator/mojom/memory_coordinator_diagnostics.mojom",
  "content/common/navigation_client.mojom",
  "content/common/render_message_filter.mojom",
  "content/common/render_widget_host_ns_view.mojom",
  "content/common/renderer.mojom",
  "content/common/renderer_host.mojom",
  "content/common/renderer_variations_configuration.mojom"
]
def pathBlock12 : Array String := #[
  "content/common/sandbox_support.mojom",
  "content/common/synthetic_trial_configuration.mojom",
  "content/common/thread_type_switcher.mojom",
  "content/common/web_contents_ns_view_bridge.mojom",
  "content/common/web_ui.mojom",
  "content/public/common/alternative_error_page_override_info.mojom",
  "content/public/common/drop_data.mojom",
  "content/public/common/extra_mojo_js_features.mojom",
  "content/public/common/font_cache_win.mojom",
  "content/public/common/media_playback_renderer_type.mojom",
  "content/public/common/resource_usage_reporter.mojom",
  "content/public/common/webplugininfo.mojom",
  "content/public/common/window_container_type.mojom",
  "content/public/test/mojo_capability_control_test_interfaces.mojom",
  "content/public/test/test_service.mojom",
  "content/services/devtools_media_encoding_service/public/mojom/devtools_media_encoding_service.mojom",
  "content/services/resource_broker/public/mojom/resource_broker.mojom",
  "content/shell/common/main_frame_counter_test.mojom",
  "content/shell/common/memory_coordinator/memory_coordinator_test.mojom",
  "content/shell/common/power_monitor_test.mojom",
  "content/shell/common/render_frame_test_helper.mojom",
  "content/test/frame_host_test_interface.mojom",
  "content/utility/sandbox_delegate_data.mojom",
  "content/web_test/common/fake_bluetooth_chooser.mojom",
  "content/web_test/common/mojo_echo.mojom",
  "content/web_test/common/mojo_optional_numerics_unittest.mojom",
  "content/web_test/common/web_test.mojom",
  "content/web_test/common/web_test_bluetooth_fake_adapter_setter.mojom",
  "device/bluetooth/public/mojom/adapter.mojom",
  "device/bluetooth/public/mojom/device.mojom",
  "device/bluetooth/public/mojom/emulation/fake_bluetooth.mojom",
  "device/bluetooth/public/mojom/gatt_characteristic_permissions.mojom",
  "device/bluetooth/public/mojom/gatt_characteristic_properties.mojom",
  "device/bluetooth/public/mojom/gatt_service_error_code.mojom",
  "device/bluetooth/public/mojom/uuid.mojom",
  "device/gamepad/public/mojom/gamepad.mojom",
  "device/vr/public/mojom/isolated_xr_service.mojom",
  "device/vr/public/mojom/openxr_interaction_profile_type.mojom",
  "device/vr/public/mojom/vr_service.mojom",
  "device/vr/public/mojom/xr_device.mojom",
  "device/vr/public/mojom/xr_hand_tracking_data.mojom",
  "device/vr/public/mojom/xr_session.mojom",
  "extensions/common/api/mime_handler.mojom",
  "extensions/common/mojom/activation_sequence.mojom",
  "extensions/common/mojom/api_permission_id.mojom",
  "extensions/common/mojom/app_window.mojom",
  "extensions/common/mojom/automation_registry.mojom",
  "extensions/common/mojom/channel.mojom",
  "extensions/common/mojom/code_injection.mojom",
  "extensions/common/mojom/context_type.mojom",
  "extensions/common/mojom/css_origin.mojom",
  "extensions/common/mojom/event_dispatcher.mojom",
  "extensions/common/mojom/event_router.mojom",
  "extensions/common/mojom/execution_world.mojom",
  "extensions/common/mojom/extension_id.mojom",
  "extensions/common/mojom/extra_response_data.mojom",
  "extensions/common/mojom/feature_session_type.mojom",
  "extensions/common/mojom/frame.mojom",
  "extensions/common/mojom/guest_view.mojom",
  "extensions/common/mojom/host_id.mojom",
  "extensions/common/mojom/injection_type.mojom",
  "extensions/common/mojom/keep_alive.mojom",
  "extensions/common/mojom/manifest.mojom",
  "extensions/common/mojom/match_origin_as_fallback.mojom"
]
def pathBlock13 : Array String := #[
  "extensions/common/mojom/message_port.mojom",
  "extensions/common/mojom/permission_set.mojom",
  "extensions/common/mojom/renderer.mojom",
  "extensions/common/mojom/renderer_host.mojom",
  "extensions/common/mojom/run_location.mojom",
  "extensions/common/mojom/service_worker.mojom",
  "extensions/common/mojom/service_worker_host.mojom",
  "extensions/common/mojom/stack_frame.mojom",
  "extensions/common/mojom/url_pattern_set.mojom",
  "extensions/common/mojom/view_type.mojom",
  "extensions/common/mojom/web_request_host.mojom",
  "fuchsia_web/webengine/mojom/web_engine_media_resource_provider.mojom",
  "gpu/ipc/common/capabilities.mojom",
  "gpu/ipc/common/constants.mojom",
  "gpu/ipc/common/context_result.mojom",
  "gpu/ipc/common/context_type.mojom",
  "gpu/ipc/common/device_perf_info.mojom",
  "gpu/ipc/common/exported_shared_image.mojom",
  "gpu/ipc/common/gpu_channel.mojom",
  "gpu/ipc/common/gpu_disk_cache_type.mojom",
  "gpu/ipc/common/gpu_feature_info.mojom",
  "gpu/ipc/common/gpu_info.mojom",
  "gpu/ipc/common/gpu_peak_memory.mojom",
  "gpu/ipc/common/gpu_preferences.mojom",
  "gpu/ipc/common/luid.mojom",
  "gpu/ipc/common/mailbox.mojom",
  "gpu/ipc/common/memory_stats.mojom",
  "gpu/ipc/common/shared_image_capabilities.mojom",
  "gpu/ipc/common/shared_image_metadata.mojom",
  "gpu/ipc/common/shared_image_pool_client_interface.mojom",
  "gpu/ipc/common/shared_image_pool_id.mojom",
  "gpu/ipc/common/surface_handle.mojom",
  "gpu/ipc/common/sync_token.mojom",
  "gpu/ipc/common/vulkan_info.mojom",
  "gpu/ipc/common/vulkan_types.mojom",
  "gpu/ipc/common/vulkan_ycbcr_info.mojom",
  "ios/chrome/browser/optimization_guide/mojom/ai_prototyping_service.mojom",
  "ios/chrome/browser/optimization_guide/mojom/enhanced_calendar_service.mojom",
  "ios/chrome/browser/optimization_guide/mojom/model_led_suggestions_service.mojom",
  "ios/chrome/browser/optimization_guide/mojom/smart_tab_grouping_service.mojom",
  "ios/chrome/browser/optimization_guide/mojom/tab_organization_service.mojom",
  "ios/chrome/browser/webui/ui_bundled/inspect/inspect.mojom",
  "ios/web/shell/web_usage_controller.mojom",
  "ipc/constants.mojom",
  "ipc/ipc.mojom",
  "media/capture/mojom/image_capture.mojom",
  "media/capture/mojom/video_capture.mojom",
  "media/capture/mojom/video_capture_buffer.mojom",
  "media/capture/mojom/video_capture_types.mojom",
  "media/capture/video/chromeos/mojom/camera3.mojom",
  "media/capture/video/chromeos/mojom/camera_app.mojom",
  "media/capture/video/chromeos/mojom/camera_common.mojom",
  "media/capture/video/chromeos/mojom/camera_features.mojom",
  "media/capture/video/chromeos/mojom/camera_metadata.mojom",
  "media/capture/video/chromeos/mojom/camera_metadata_tags.mojom",
  "media/capture/video/chromeos/mojom/cros_camera_client.mojom",
  "media/capture/video/chromeos/mojom/cros_camera_service.mojom",
  "media/capture/video/chromeos/mojom/document_scanner.mojom",
  "media/capture/video/chromeos/mojom/effects_pipeline.mojom",
  "media/capture/video/chromeos/mojom/jpeg_accelerator.mojom",
  "media/capture/video/chromeos/mojom/system_event_monitor.mojom",
  "media/capture/video/chromeos/mojom/video_capture_device_info_monitor.mojom",
  "media/midi/midi_service.mojom",
  "media/mojo/mojom/android_overlay.mojom"
]
def pathBlock14 : Array String := #[
  "media/mojo/mojom/audio_data.mojom",
  "media/mojo/mojom/audio_data_pipe.mojom",
  "media/mojo/mojom/audio_decoder.mojom",
  "media/mojo/mojom/audio_encoder.mojom",
  "media/mojo/mojom/audio_input_stream.mojom",
  "media/mojo/mojom/audio_logging.mojom",
  "media/mojo/mojom/audio_output_stream.mojom",
  "media/mojo/mojom/audio_parameters.mojom",
  "media/mojo/mojom/audio_processing.mojom",
  "media/mojo/mojom/audio_stream_factory.mojom",
  "media/mojo/mojom/capture_handle.mojom",
  "media/mojo/mojom/cast_application_media_info_manager.mojom",
  "media/mojo/mojom/cdm_context_for_oopvd.mojom",
  "media/mojo/mojom/cdm_document_service.mojom",
  "media/mojo/mojom/cdm_service.mojom",
  "media/mojo/mojom/cdm_storage.mojom",
  "media/mojo/mojom/channel_layout.mojom",
  "media/mojo/mojom/content_decryption_module.mojom",
  "media/mojo/mojom/dcomp_surface_registry.mojom",
  "media/mojo/mojom/decryptor.mojom",
  "media/mojo/mojom/demuxer_stream.mojom",
  "media/mojo/mojom/display_media_information.mojom",
  "media/mojo/mojom/encryption_pattern.mojom",
  "media/mojo/mojom/frame_interface_factory.mojom",
  "media/mojo/mojom/fuchsia_media.mojom",
  "media/mojo/mojom/interface_factory.mojom",
  "media/mojo/mojom/key_system_support.mojom",
  "media/mojo/mojom/media_drm_storage.mojom",
  "media/mojo/mojom/media_foundation_preferences.mojom",
  "media/mojo/mojom/media_foundation_service.mojom",
  "media/mojo/mojom/media_log.mojom",
  "media/mojo/mojom/media_metrics_provider.mojom",
  "media/mojo/mojom/media_player.mojom",
  "media/mojo/mojom/media_service.mojom",
  "media/mojo/mojom/media_types.mojom",
  "media/mojo/mojom/mediadrm_support.mojom",
  "media/mojo/mojom/output_protection.mojom",
  "media/mojo/mojom/playback_events_recorder.mojom",
  "media/mojo/mojom/provision_fetcher.mojom",
  "media/mojo/mojom/remoting.mojom",
  "media/mojo/mojom/remoting_common.mojom",
  "media/mojo/mojom/renderer.mojom",
  "media/mojo/mojom/renderer_extensions.mojom",
  "media/mojo/mojom/speech_recognition.mojom",
  "media/mojo/mojom/speech_recognition_audio_forwarder.mojom",
  "media/mojo/mojom/speech_recognition_error.mojom",
  "media/mojo/mojom/speech_recognition_error_code.mojom",
  "media/mojo/mojom/speech_recognition_grammar.mojom",
  "media/mojo/mojom/speech_recognition_recognition_context.mojom",
  "media/mojo/mojom/speech_recognition_result.mojom",
  "media/mojo/mojom/speech_recognition_service.mojom",
  "media/mojo/mojom/speech_recognizer.mojom",
  "media/mojo/mojom/stable/native_pixmap_handle.mojom",
  "media/mojo/mojom/video_decode_perf_history.mojom",
  "media/mojo/mojom/video_decode_stats_recorder.mojom",
  "media/mojo/mojom/video_decoder.mojom",
  "media/mojo/mojom/video_decoder_factory_process.mojom",
  "media/mojo/mojom/video_encode_accelerator.mojom",
  "media/mojo/mojom/video_encoder_info.mojom",
  "media/mojo/mojom/video_encoder_metrics_provider.mojom",
  "media/mojo/mojom/watch_time_recorder.mojom",
  "media/mojo/mojom/webrtc_video_perf.mojom",
  "mojo/public/interfaces/bindings/interface_control_messages.mojom",
  "mojo/public/interfaces/bindings/native_struct.mojom"
]
def pathBlock15 : Array String := #[
  "mojo/public/interfaces/bindings/pipe_control_messages.mojom",
  "mojo/public/mojom/base/absl_status.mojom",
  "mojo/public/mojom/base/application_state.mojom",
  "mojo/public/mojom/base/battery_power_status.mojom",
  "mojo/public/mojom/base/big_buffer.mojom",
  "mojo/public/mojom/base/big_string.mojom",
  "mojo/public/mojom/base/binder.mojom",
  "mojo/public/mojom/base/byte_size.mojom",
  "mojo/public/mojom/base/byte_string.mojom",
  "mojo/public/mojom/base/empty.mojom",
  "mojo/public/mojom/base/error.mojom",
  "mojo/public/mojom/base/file.mojom",
  "mojo/public/mojom/base/file_error.mojom",
  "mojo/public/mojom/base/file_info.mojom",
  "mojo/public/mojom/base/file_path.mojom",
  "mojo/public/mojom/base/generic_pending_associated_receiver.mojom",
  "mojo/public/mojom/base/generic_pending_receiver.mojom",
  "mojo/public/mojom/base/int128.mojom",
  "mojo/public/mojom/base/jserror.mojom",
  "mojo/public/mojom/base/language_tag.mojom",
  "mojo/public/mojom/base/logfont_win.mojom",
  "mojo/public/mojom/base/memory_allocator_dump_cross_process_uid.mojom",
  "mojo/public/mojom/base/memory_limit.mojom",
  "mojo/public/mojom/base/memory_pressure_level.mojom",
  "mojo/public/mojom/base/message_pump_type.mojom",
  "mojo/public/mojom/base/process_id.mojom",
  "mojo/public/mojom/base/process_priority.mojom",
  "mojo/public/mojom/base/proto_wrapper.mojom",
  "mojo/public/mojom/base/read_only_buffer.mojom",
  "mojo/public/mojom/base/ref_counted_memory.mojom",
  "mojo/public/mojom/base/safe_base_name.mojom",
  "mojo/public/mojom/base/shared_memory.mojom",
  "mojo/public/mojom/base/string16.mojom",
  "mojo/public/mojom/base/text_direction.mojom",
  "mojo/public/mojom/base/thread_type.mojom",
  "mojo/public/mojom/base/time.mojom",
  "mojo/public/mojom/base/token.mojom",
  "mojo/public/mojom/base/unguessable_token.mojom",
  "mojo/public/mojom/base/uuid.mojom",
  "mojo/public/mojom/base/values.mojom",
  "mojo/public/mojom/base/version.mojom",
  "mojo/public/mojom/base/work_in_progress.mojom",
  "mojo/public/mojom/base/wstring.mojom",
  "mojo/public/tools/fuzzers/fuzz.mojom",
  "pdf/mojom/pdf.mojom",
  "printing/backend/mojom/print_backend.mojom",
  "printing/mojom/print.mojom",
  "printing/mojom/printing_context.mojom",
  "remoting/host/mojom/agent_process_broker.mojom",
  "remoting/host/mojom/chromoting_host_services.mojom",
  "remoting/host/mojom/common.mojom",
  "remoting/host/mojom/desktop_session.mojom",
  "remoting/host/mojom/keyboard_layout.mojom",
  "remoting/host/mojom/login_session.mojom",
  "remoting/host/mojom/peer_session.mojom",
  "remoting/host/mojom/remote_security_key.mojom",
  "remoting/host/mojom/remote_support.mojom",
  "remoting/host/mojom/remote_url_opener.mojom",
  "remoting/host/mojom/remoting_host.mojom",
  "remoting/host/mojom/webauthn_proxy.mojom",
  "remoting/host/mojom/webrtc_types.mojom",
  "sandbox/mac/mojom/seatbelt_extension_token.mojom",
  "sandbox/mac/mojom/traits_test_service.mojom",
  "sandbox/policy/mojom/context.mojom"
]
def pathBlock16 : Array String := #[
  "sandbox/policy/mojom/sandbox.mojom",
  "services/accessibility/android/public/mojom/accessibility_helper.mojom",
  "services/accessibility/public/mojom/assistive_technology_type.mojom",
  "services/accessibility/public/mojom/automation.mojom",
  "services/audio/public/mojom/audio_device_description.mojom",
  "services/audio/public/mojom/audio_service.mojom",
  "services/audio/public/mojom/debug_recording.mojom",
  "services/audio/public/mojom/device_notifications.mojom",
  "services/audio/public/mojom/log_factory_manager.mojom",
  "services/audio/public/mojom/ml_model_manager.mojom",
  "services/audio/public/mojom/system_info.mojom",
  "services/audio/public/mojom/testing_api.mojom",
  "services/cert_verifier/public/mojom/cert_verifier_service_factory.mojom",
  "services/data_decoder/public/mojom/data_decoder_service.mojom",
  "services/data_decoder/public/mojom/gzipper.mojom",
  "services/data_decoder/public/mojom/image_decoder.mojom",
  "services/data_decoder/public/mojom/structured_headers_parser.mojom",
  "services/data_decoder/public/mojom/xml_parser.mojom",
  "services/device/public/mojom/battery_monitor.mojom",
  "services/device/public/mojom/battery_status.mojom",
  "services/device/public/mojom/device_service.mojom",
  "services/device/public/mojom/fingerprint.mojom",
  "services/device/public/mojom/geolocation.mojom",
  "services/device/public/mojom/geolocation_client_id.mojom",
  "services/device/public/mojom/geolocation_context.mojom",
  "services/device/public/mojom/geolocation_control.mojom",
  "services/device/public/mojom/geolocation_internals.mojom",
  "services/device/public/mojom/geoposition.mojom",
  "services/device/public/mojom/haptics.mojom",
  "services/device/public/mojom/hid.mojom",
  "services/device/public/mojom/input_service.mojom",
  "services/device/public/mojom/mtp_file_entry.mojom",
  "services/device/public/mojom/mtp_manager.mojom",
  "services/device/public/mojom/mtp_storage_info.mojom",
  "services/device/public/mojom/nfc.mojom",
  "services/device/public/mojom/nfc_provider.mojom",
  "services/device/public/mojom/power_monitor.mojom",
  "services/device/public/mojom/pressure_manager.mojom",
  "services/device/public/mojom/pressure_update.mojom",
  "services/device/public/mojom/public_ip_address_geolocation_provider.mojom",
  "services/device/public/mojom/screen_orientation.mojom",
  "services/device/public/mojom/screen_orientation_lock_types.mojom",
  "services/device/public/mojom/sensor.mojom",
  "services/device/public/mojom/sensor_provider.mojom",
  "services/device/public/mojom/serial.mojom",
  "services/device/public/mojom/smart_card.mojom",
  "services/device/public/mojom/time_zone_monitor.mojom",
  "services/device/public/mojom/usb_device.mojom",
  "services/device/public/mojom/usb_enumeration_options.mojom",
  "services/device/public/mojom/usb_manager.mojom",
  "services/device/public/mojom/usb_manager_client.mojom",
  "services/device/public/mojom/usb_manager_test.mojom",
  "services/device/public/mojom/vibration_manager.mojom",
  "services/device/public/mojom/wake_lock.mojom",
  "services/device/public/mojom/wake_lock_context.mojom",
  "services/device/public/mojom/wake_lock_provider.mojom",
  "services/image_annotation/public/mojom/image_annotation.mojom",
  "services/media_session/public/mojom/audio_focus.mojom",
  "services/media_session/public/mojom/constants.mojom",
  "services/media_session/public/mojom/media_controller.mojom",
  "services/media_session/public/mojom/media_session.mojom",
  "services/media_session/public/mojom/media_session_service.mojom",
  "services/metrics/public/mojom/ukm_interface.mojom",
  "services/network/public/cpp/network_traits_test_service.mojom"
]
def pathBlock17 : Array String := #[
  "services/network/public/mojom/accept_ch_frame_observer.mojom",
  "services/network/public/mojom/address_family.mojom",
  "services/network/public/mojom/address_list.mojom",
  "services/network/public/mojom/alternate_protocol_usage.mojom",
  "services/network/public/mojom/auth.mojom",
  "services/network/public/mojom/blocked_by_response_reason.mojom",
  "services/network/public/mojom/cache_encryption_provider.mojom",
  "services/network/public/mojom/cache_storage_side_data_writer.mojom",
  "services/network/public/mojom/cert_verifier_service.mojom",
  "services/network/public/mojom/cert_verifier_service_updater.mojom",
  "services/network/public/mojom/cert_verify_result.mojom",
  "services/network/public/mojom/chunked_data_pipe_getter.mojom",
  "services/network/public/mojom/clear_data_filter.mojom",
  "services/network/public/mojom/client_security_state.mojom",
  "services/network/public/mojom/connection_allowlist.mojom",
  "services/network/public/mojom/connection_change_observer_client.mojom",
  "services/network/public/mojom/connection_endpoint_metadata.mojom",
  "services/network/public/mojom/content_security_policy.mojom",
  "services/network/public/mojom/cookie_access_observer.mojom",
  "services/network/public/mojom/cookie_encryption_provider.mojom",
  "services/network/public/mojom/cookie_manager.mojom",
  "services/network/public/mojom/cookie_partition_key.mojom",
  "services/network/public/mojom/cookie_setting_overrides.mojom",
  "services/network/public/mojom/cors.mojom",
  "services/network/public/mojom/cors_origin_pattern.mojom",
  "services/network/public/mojom/cross_origin_embedder_policy.mojom",
  "services/network/public/mojom/cross_origin_opener_policy.mojom",
  "services/network/public/mojom/ct_log_info.mojom",
  "services/network/public/mojom/ct_policy.mojom",
  "services/network/public/mojom/ct_policy_status.mojom",
  "services/network/public/mojom/data_pipe_getter.mojom",
  "services/network/public/mojom/declarative_performance_observer.mojom",
  "services/network/public/mojom/default_credentials.mojom",
  "services/network/public/mojom/device_bound_sessions.mojom",
  "services/network/public/mojom/devtools_observer.mojom",
  "services/network/public/mojom/dhcp_wpad_url_client.mojom",
  "services/network/public/mojom/document_isolation_policy.mojom",
  "services/network/public/mojom/early_hints.mojom",
  "services/network/public/mojom/encoded_body_length.mojom",
  "services/network/public/mojom/fetch_api.mojom",
  "services/network/public/mojom/fetch_retry_options.mojom",
  "services/network/public/mojom/hash_value.mojom",
  "services/network/public/mojom/host_resolver.mojom",
  "services/network/public/mojom/host_resolver_endpoint_result.mojom",
  "services/network/public/mojom/http_cache_backend_file_operations.mojom",
  "services/network/public/mojom/http_raw_headers.mojom",
  "services/network/public/mojom/http_request_headers.mojom",
  "services/network/public/mojom/http_response_headers.mojom",
  "services/network/public/mojom/integrity_algorithm.mojom",
  "services/network/public/mojom/integrity_metadata.mojom",
  "services/network/public/mojom/integrity_policy.mojom",
  "services/network/public/mojom/ip_address.mojom",
  "services/network/public/mojom/ip_address_space.mojom",
  "services/network/public/mojom/ip_endpoint.mojom",
  "services/network/public/mojom/isolation_info.mojom",
  "services/network/public/mojom/key_pinning.mojom",
  "services/network/public/mojom/link_header.mojom",
  "services/network/public/mojom/load_timing_info.mojom",
  "services/network/public/mojom/load_timing_internal_info.mojom",
  "services/network/public/mojom/mdns_responder.mojom",
  "services/network/public/mojom/mutable_network_traffic_annotation_tag.mojom",
  "services/network/public/mojom/mutable_partial_network_traffic_annotation_tag.mojom",
  "services/network/public/mojom/net_log.mojom",
  "services/network/public/mojom/network_annotation_monitor.mojom"
]
def pathBlock18 : Array String := #[
  "services/network/public/mojom/network_anonymization_key.mojom",
  "services/network/public/mojom/network_change_manager.mojom",
  "services/network/public/mojom/network_context.mojom",
  "services/network/public/mojom/network_context_client.mojom",
  "services/network/public/mojom/network_interface.mojom",
  "services/network/public/mojom/network_interface_change_listener.mojom",
  "services/network/public/mojom/network_isolation_key.mojom",
  "services/network/public/mojom/network_isolation_partition.mojom",
  "services/network/public/mojom/network_param.mojom",
  "services/network/public/mojom/network_quality_estimator_manager.mojom",
  "services/network/public/mojom/network_service.mojom",
  "services/network/public/mojom/network_service_test.mojom",
  "services/network/public/mojom/network_types.mojom",
  "services/network/public/mojom/no_vary_search.mojom",
  "services/network/public/mojom/oblivious_http_request.mojom",
  "services/network/public/mojom/ocsp_verify_result.mojom",
  "services/network/public/mojom/origin_or_wildcard_header_value.mojom",
  "services/network/public/mojom/originating_process_id.mojom",
  "services/network/public/mojom/p2p.mojom",
  "services/network/public/mojom/p2p_trusted.mojom",
  "services/network/public/mojom/parsed_headers.mojom",
  "services/network/public/mojom/parsed_request_cookie.mojom",
  "services/network/public/mojom/permissions_policy/permissions_policy.mojom",
  "services/network/public/mojom/permissions_policy/permissions_policy_feature.mojom",
  "services/network/public/mojom/proxy_config.mojom",
  "services/network/public/mojom/proxy_config_with_annotation.mojom",
  "services/network/public/mojom/proxy_lookup_client.mojom",
  "services/network/public/mojom/proxy_resolving_socket.mojom",
  "services/network/public/mojom/referrer_policy.mojom",
  "services/network/public/mojom/reporting_service.mojom",
  "services/network/public/mojom/request_priority.mojom",
  "services/network/public/mojom/restricted_cookie_manager.mojom",
  "services/network/public/mojom/restricted_device_bound_sessions.mojom",
  "services/network/public/mojom/restricted_udp_socket.mojom",
  "services/network/public/mojom/schemeful_site.mojom",
  "services/network/public/mojom/sct_status_flags.mojom",
  "services/network/public/mojom/service_worker_router_info.mojom",
  "services/network/public/mojom/shared_dictionary_access_observer.mojom",
  "services/network/public/mojom/shared_dictionary_error.mojom",
  "services/network/public/mojom/shared_dictionary_isolation_key.mojom",
  "services/network/public/mojom/shared_dictionary_usage_info.mojom",
  "services/network/public/mojom/shared_http_cache_client.mojom",
  "services/network/public/mojom/signed_certificate_timestamp.mojom",
  "services/network/public/mojom/signed_certificate_timestamp_and_status.mojom",
  "services/network/public/mojom/site_for_cookies.mojom",
  "services/network/public/mojom/socket_broker.mojom",
  "services/network/public/mojom/socket_connection_tracker.mojom",
  "services/network/public/mojom/socket_factory.mojom",
  "services/network/public/mojom/source_location.mojom",
  "services/network/public/mojom/source_type.mojom",
  "services/network/public/mojom/sri_message_signature.mojom",
  "services/network/public/mojom/ssl_config.mojom",
  "services/network/public/mojom/ssl_info.mojom",
  "services/network/public/mojom/storage_access_api.mojom",
  "services/network/public/mojom/structured_headers.mojom",
  "services/network/public/mojom/supports_loading_mode.mojom",
  "services/network/public/mojom/system_dns_resolution.mojom",
  "services/network/public/mojom/tcp_socket.mojom",
  "services/network/public/mojom/timing_allow_origin.mojom",
  "services/network/public/mojom/tls_socket.mojom",
  "services/network/public/mojom/transferable_directory.mojom",
  "services/network/public/mojom/transferable_socket.mojom",
  "services/network/public/mojom/trust_token_access_observer.mojom",
  "services/network/public/mojom/trust_tokens.mojom"
]
def pathBlock19 : Array String := #[
  "services/network/public/mojom/udp_socket.mojom",
  "services/network/public/mojom/unencoded_digest.mojom",
  "services/network/public/mojom/url_loader.mojom",
  "services/network/public/mojom/url_loader_completion_status.mojom",
  "services/network/public/mojom/url_loader_factory.mojom",
  "services/network/public/mojom/url_loader_network_service_observer.mojom",
  "services/network/public/mojom/url_request.mojom",
  "services/network/public/mojom/url_response_head.mojom",
  "services/network/public/mojom/web_bundle_handle.mojom",
  "services/network/public/mojom/web_client_hints_types.mojom",
  "services/network/public/mojom/web_sandbox_flags.mojom",
  "services/network/public/mojom/web_transport.mojom",
  "services/network/public/mojom/websocket.mojom",
  "services/network/public/mojom/x509_certificate.mojom",
  "services/network/public/mojom/x_frame_options.mojom",
  "services/on_device_model/android/downloader_params.mojom",
  "services/on_device_model/public/mojom/download_observer.mojom",
  "services/on_device_model/public/mojom/on_device_model.mojom",
  "services/on_device_model/public/mojom/on_device_model_service.mojom",
  "services/passage_embeddings/public/mojom/passage_embeddings.mojom",
  "services/preferences/public/mojom/preferences.mojom",
  "services/preferences/public/mojom/tracked_preference_validation_delegate.mojom",
  "services/proxy_resolver/public/mojom/proxy_resolver.mojom",
  "services/proxy_resolver/public/mojom/system_proxy_resolver.mojom",
  "services/resource_coordinator/public/mojom/memory_instrumentation/constants.mojom",
  "services/resource_coordinator/public/mojom/memory_instrumentation/memory_instrumentation.mojom",
  "services/screen_ai/public/mojom/screen_ai_factory.mojom",
  "services/screen_ai/public/mojom/screen_ai_service.mojom",
  "services/service_manager/public/mojom/connector.mojom",
  "services/service_manager/public/mojom/constants.mojom",
  "services/service_manager/public/mojom/interface_provider.mojom",
  "services/service_manager/public/mojom/interface_provider_spec.mojom",
  "services/service_manager/public/mojom/service.mojom",
  "services/service_manager/public/mojom/service_control.mojom",
  "services/service_manager/public/mojom/service_filter.mojom",
  "services/service_manager/public/mojom/service_manager.mojom",
  "services/shape_detection/public/mojom/barcodedetection.mojom",
  "services/shape_detection/public/mojom/barcodedetection_provider.mojom",
  "services/shape_detection/public/mojom/facedetection.mojom",
  "services/shape_detection/public/mojom/facedetection_provider.mojom",
  "services/shape_detection/public/mojom/shape_detection_service.mojom",
  "services/shape_detection/public/mojom/textdetection.mojom",
  "services/test/echo/public/mojom/echo.mojom",
  "services/tracing/public/mojom/background_tracing_agent.mojom",
  "services/tracing/public/mojom/constants.mojom",
  "services/tracing/public/mojom/perfetto_service.mojom",
  "services/tracing/public/mojom/system_tracing_service.mojom",
  "services/tracing/public/mojom/traced_process.mojom",
  "services/tracing/public/mojom/tracing_service.mojom",
  "services/video_capture/public/mojom/constants.mojom",
  "services/video_capture/public/mojom/device.mojom",
  "services/video_capture/public/mojom/devices_changed_observer.mojom",
  "services/video_capture/public/mojom/producer.mojom",
  "services/video_capture/public/mojom/testing_controls.mojom",
  "services/video_capture/public/mojom/video_capture_service.mojom",
  "services/video_capture/public/mojom/video_frame_handler.mojom",
  "services/video_capture/public/mojom/video_source.mojom",
  "services/video_capture/public/mojom/video_source_provider.mojom",
  "services/video_capture/public/mojom/virtual_device.mojom",
  "services/viz/privileged/mojom/compositing/begin_frame_observer.mojom",
  "services/viz/privileged/mojom/compositing/display_private.mojom",
  "services/viz/privileged/mojom/compositing/external_begin_frame_controller.mojom",
  "services/viz/privileged/mojom/compositing/features.mojom",
  "services/viz/privileged/mojom/compositing/frame_sink_manager.mojom"
]
def pathBlock20 : Array String := #[
  "services/viz/privileged/mojom/compositing/frame_sink_manager_test_api.mojom",
  "services/viz/privileged/mojom/compositing/frame_sink_video_capture.mojom",
  "services/viz/privileged/mojom/compositing/frame_sinks_metrics_recorder.mojom",
  "services/viz/privileged/mojom/compositing/layered_window_updater.mojom",
  "services/viz/privileged/mojom/compositing/overlay_strategy.mojom",
  "services/viz/privileged/mojom/compositing/renderer_settings.mojom",
  "services/viz/privileged/mojom/compositing/vsync_parameter_observer.mojom",
  "services/viz/privileged/mojom/gl/context_lost_reason.mojom",
  "services/viz/privileged/mojom/gl/gpu_client_type.mojom",
  "services/viz/privileged/mojom/gl/gpu_host.mojom",
  "services/viz/privileged/mojom/gl/gpu_logging.mojom",
  "services/viz/privileged/mojom/gl/gpu_service.mojom",
  "services/viz/privileged/mojom/gl/info_collection_gpu_service.mojom",
  "services/viz/privileged/mojom/viz_main.mojom",
  "services/viz/public/mojom/compositing/animation.mojom",
  "services/viz/public/mojom/compositing/begin_frame_args.mojom",
  "services/viz/public/mojom/compositing/bitmap_in_shared_memory.mojom",
  "services/viz/public/mojom/compositing/blit_request.mojom",
  "services/viz/public/mojom/compositing/compositing_mode_watcher.mojom",
  "services/viz/public/mojom/compositing/compositor_frame.mojom",
  "services/viz/public/mojom/compositing/compositor_frame_metadata.mojom",
  "services/viz/public/mojom/compositing/compositor_frame_sink.mojom",
  "services/viz/public/mojom/compositing/compositor_frame_transition_directive.mojom",
  "services/viz/public/mojom/compositing/compositor_render_pass.mojom",
  "services/viz/public/mojom/compositing/compositor_render_pass_id.mojom",
  "services/viz/public/mojom/compositing/copy_output_request.mojom",
  "services/viz/public/mojom/compositing/copy_output_result.mojom",
  "services/viz/public/mojom/compositing/filter_operation.mojom",
  "services/viz/public/mojom/compositing/filter_operations.mojom",
  "services/viz/public/mojom/compositing/frame_deadline.mojom",
  "services/viz/public/mojom/compositing/frame_interval_inputs.mojom",
  "services/viz/public/mojom/compositing/frame_sink_bundle.mojom",
  "services/viz/public/mojom/compositing/frame_sink_bundle_id.mojom",
  "services/viz/public/mojom/compositing/frame_sink_id.mojom",
  "services/viz/public/mojom/compositing/frame_timing_details.mojom",
  "services/viz/public/mojom/compositing/internal/singleplanar_format.mojom",
  "services/viz/public/mojom/compositing/layer.mojom",
  "services/viz/public/mojom/compositing/layer_context.mojom",
  "services/viz/public/mojom/compositing/local_surface_id.mojom",
  "services/viz/public/mojom/compositing/offset_tag.mojom",
  "services/viz/public/mojom/compositing/paint_filter.mojom",
  "services/viz/public/mojom/compositing/quads.mojom",
  "services/viz/public/mojom/compositing/region_capture_bounds.mojom",
  "services/viz/public/mojom/compositing/resource_id.mojom",
  "services/viz/public/mojom/compositing/returned_resource.mojom",
  "services/viz/public/mojom/compositing/selection.mojom",
  "services/viz/public/mojom/compositing/shared_image_format.mojom",
  "services/viz/public/mojom/compositing/shared_quad_state.mojom",
  "services/viz/public/mojom/compositing/subtree_capture_id.mojom",
  "services/viz/public/mojom/compositing/surface_id.mojom",
  "services/viz/public/mojom/compositing/surface_info.mojom",
  "services/viz/public/mojom/compositing/surface_range.mojom",
  "services/viz/public/mojom/compositing/texture_releaser.mojom",
  "services/viz/public/mojom/compositing/thread.mojom",
  "services/viz/public/mojom/compositing/tiling.mojom",
  "services/viz/public/mojom/compositing/tracked_element_rects.mojom",
  "services/viz/public/mojom/compositing/transferable_resource.mojom",
  "services/viz/public/mojom/compositing/trees_in_viz_timing.mojom",
  "services/viz/public/mojom/compositing/vertical_scroll_direction.mojom",
  "services/viz/public/mojom/compositing/video_detector_observer.mojom",
  "services/viz/public/mojom/compositing/view_transition_element_resource_id.mojom",
  "services/viz/public/mojom/compositing/view_transition_request.mojom",
  "services/viz/public/mojom/gpu.mojom",
  "services/viz/public/mojom/hit_test/aggregated_hit_test_region.mojom"
]
def pathBlock21 : Array String := #[
  "services/viz/public/mojom/hit_test/hit_test_region_list.mojom",
  "services/viz/public/mojom/hit_test/input_target_client.mojom",
  "services/webnn/public/mojom/ep_device_info.mojom",
  "services/webnn/public/mojom/ep_package_info.mojom",
  "services/webnn/public/mojom/features.mojom",
  "services/webnn/public/mojom/webnn_browser_host.mojom",
  "services/webnn/public/mojom/webnn_compiler_context.mojom",
  "services/webnn/public/mojom/webnn_compiler_service.mojom",
  "services/webnn/public/mojom/webnn_context.mojom",
  "services/webnn/public/mojom/webnn_context_properties.mojom",
  "services/webnn/public/mojom/webnn_context_provider.mojom",
  "services/webnn/public/mojom/webnn_device.mojom",
  "services/webnn/public/mojom/webnn_error.mojom",
  "services/webnn/public/mojom/webnn_graph.mojom",
  "services/webnn/public/mojom/webnn_graph_builder.mojom",
  "services/webnn/public/mojom/webnn_model_loader.mojom",
  "services/webnn/public/mojom/webnn_service_introspection.mojom",
  "services/webnn/public/mojom/webnn_tensor.mojom",
  "skia/public/mojom/bitmap.mojom",
  "skia/public/mojom/blend_mode.mojom",
  "skia/public/mojom/hdr_metadata.mojom",
  "skia/public/mojom/image_info.mojom",
  "skia/public/mojom/skcolor.mojom",
  "skia/public/mojom/skcolor4f.mojom",
  "skia/public/mojom/skcolorspace.mojom",
  "skia/public/mojom/skcolorspace_primaries.mojom",
  "skia/public/mojom/skpath.mojom",
  "skia/public/mojom/surface_origin.mojom",
  "skia/public/mojom/tile_mode.mojom",
  "storage/browser/quota/quota_internals.mojom",
  "storage/browser/quota/quota_manager_observer.mojom",
  "third_party/blink/public/mojom/ad_tagging/ad_evidence.mojom",
  "third_party/blink/public/mojom/ai/ai_common.mojom",
  "third_party/blink/public/mojom/ai/ai_decision_model.mojom",
  "third_party/blink/public/mojom/ai/ai_language_model.mojom",
  "third_party/blink/public/mojom/ai/ai_manager.mojom",
  "third_party/blink/public/mojom/ai/ai_proofreader.mojom",
  "third_party/blink/public/mojom/ai/ai_rewriter.mojom",
  "third_party/blink/public/mojom/ai/ai_semantic_embedder.mojom",
  "third_party/blink/public/mojom/ai/ai_summarizer.mojom",
  "third_party/blink/public/mojom/ai/ai_writer.mojom",
  "third_party/blink/public/mojom/ai/model_streaming_responder.mojom",
  "third_party/blink/public/mojom/android_font_lookup/android_font_lookup.mojom",
  "third_party/blink/public/mojom/annotation/annotation.mojom",
  "third_party/blink/public/mojom/app_banner/app_banner.mojom",
  "third_party/blink/public/mojom/array_buffer/array_buffer_contents.mojom",
  "third_party/blink/public/mojom/associated_interfaces/associated_interfaces.mojom",
  "third_party/blink/public/mojom/autoplay/autoplay.mojom",
  "third_party/blink/public/mojom/back_forward_cache_not_restored_reasons.mojom",
  "third_party/blink/public/mojom/background_fetch/background_fetch.mojom",
  "third_party/blink/public/mojom/background_sync/background_sync.mojom",
  "third_party/blink/public/mojom/badging/badging.mojom",
  "third_party/blink/public/mojom/blob/blob.mojom",
  "third_party/blink/public/mojom/blob/blob_registry.mojom",
  "third_party/blink/public/mojom/blob/blob_url_store.mojom",
  "third_party/blink/public/mojom/blob/data_element.mojom",
  "third_party/blink/public/mojom/blob/file_backed_blob_factory.mojom",
  "third_party/blink/public/mojom/blob/serialized_blob.mojom",
  "third_party/blink/public/mojom/bluetooth/web_bluetooth.mojom",
  "third_party/blink/public/mojom/broadcastchannel/broadcast_channel.mojom",
  "third_party/blink/public/mojom/browser_interface_broker.mojom",
  "third_party/blink/public/mojom/buckets/bucket_manager_host.mojom",
  "third_party/blink/public/mojom/cache_storage/cache_storage.mojom",
  "third_party/blink/public/mojom/call_stack_generator/call_stack_generator.mojom"
]
def pathBlock22 : Array String := #[
  "third_party/blink/public/mojom/choosers/color_chooser.mojom",
  "third_party/blink/public/mojom/choosers/date_time_chooser.mojom",
  "third_party/blink/public/mojom/choosers/file_chooser.mojom",
  "third_party/blink/public/mojom/choosers/popup_menu.mojom",
  "third_party/blink/public/mojom/clipboard/clipboard.mojom",
  "third_party/blink/public/mojom/close_watcher/close_listener.mojom",
  "third_party/blink/public/mojom/commit_result/commit_result.mojom",
  "third_party/blink/public/mojom/compute_pressure/web_pressure_manager.mojom",
  "third_party/blink/public/mojom/compute_pressure/web_pressure_update.mojom",
  "third_party/blink/public/mojom/confidence_level.mojom",
  "third_party/blink/public/mojom/contacts/contacts_manager.mojom",
  "third_party/blink/public/mojom/content_extraction/ai_page_content.mojom",
  "third_party/blink/public/mojom/content_extraction/ai_page_content_metadata.mojom",
  "third_party/blink/public/mojom/content_extraction/frame_metadata_observer_registry.mojom",
  "third_party/blink/public/mojom/content_extraction/inner_html.mojom",
  "third_party/blink/public/mojom/content_extraction/inner_text.mojom",
  "third_party/blink/public/mojom/content_extraction/script_tools.mojom",
  "third_party/blink/public/mojom/content_index/content_index.mojom",
  "third_party/blink/public/mojom/context_menu/context_menu.mojom",
  "third_party/blink/public/mojom/cookie_store/cookie_store.mojom",
  "third_party/blink/public/mojom/cpu_performance.mojom",
  "third_party/blink/public/mojom/crash/crash_memory_metrics_reporter.mojom",
  "third_party/blink/public/mojom/credentialmanagement/credential_manager.mojom",
  "third_party/blink/public/mojom/credentialmanagement/credential_type_flags.mojom",
  "third_party/blink/public/mojom/cross_origin_storage/cross_origin_storage.mojom",
  "third_party/blink/public/mojom/css/preferred_color_scheme.mojom",
  "third_party/blink/public/mojom/css/preferred_contrast.mojom",
  "third_party/blink/public/mojom/data_transfer/data_transfer.mojom",
  "third_party/blink/public/mojom/device/device.mojom",
  "third_party/blink/public/mojom/device_posture/device_posture_provider.mojom",
  "third_party/blink/public/mojom/devtools/console_message.mojom",
  "third_party/blink/public/mojom/devtools/devtools_agent.mojom",
  "third_party/blink/public/mojom/devtools/devtools_frontend.mojom",
  "third_party/blink/public/mojom/devtools/inspector_issue.mojom",
  "third_party/blink/public/mojom/dictation/dictation_agent.mojom",
  "third_party/blink/public/mojom/digital_goods/digital_goods.mojom",
  "third_party/blink/public/mojom/direct_sockets/direct_sockets.mojom",
  "third_party/blink/public/mojom/disk_allocator.mojom",
  "third_party/blink/public/mojom/document_metadata/document_metadata.mojom",
  "third_party/blink/public/mojom/dom/dom_node_id.mojom",
  "third_party/blink/public/mojom/dom_storage/dom_storage.mojom",
  "third_party/blink/public/mojom/dom_storage/session_storage_namespace.mojom",
  "third_party/blink/public/mojom/dom_storage/storage_area.mojom",
  "third_party/blink/public/mojom/drag/drag.mojom",
  "third_party/blink/public/mojom/dwrite_font_proxy/dwrite_font_proxy.mojom",
  "third_party/blink/public/mojom/facilitated_payments/payment_link_handler.mojom",
  "third_party/blink/public/mojom/favicon/favicon_url.mojom",
  "third_party/blink/public/mojom/feature_observer/feature_observer.mojom",
  "third_party/blink/public/mojom/fenced_frame/fenced_frame_config.mojom",
  "third_party/blink/public/mojom/fetch/fetch_api_request.mojom",
  "third_party/blink/public/mojom/fetch/fetch_api_response.mojom",
  "third_party/blink/public/mojom/file/file_utilities.mojom",
  "third_party/blink/public/mojom/file_system_access/file_system_access_access_handle_host.mojom",
  "third_party/blink/public/mojom/file_system_access/file_system_access_cloud_identifier.mojom",
  "third_party/blink/public/mojom/file_system_access/file_system_access_data_transfer_token.mojom",
  "third_party/blink/public/mojom/file_system_access/file_system_access_directory_handle.mojom",
  "third_party/blink/public/mojom/file_system_access/file_system_access_error.mojom",
  "third_party/blink/public/mojom/file_system_access/file_system_access_file_delegate_host.mojom",
  "third_party/blink/public/mojom/file_system_access/file_system_access_file_handle.mojom",
  "third_party/blink/public/mojom/file_system_access/file_system_access_file_modification_host.mojom",
  "third_party/blink/public/mojom/file_system_access/file_system_access_file_writer.mojom",
  "third_party/blink/public/mojom/file_system_access/file_system_access_manager.mojom",
  "third_party/blink/public/mojom/file_system_access/file_system_access_observer.mojom",
  "third_party/blink/public/mojom/file_system_access/file_system_access_observer_host.mojom"
]
def pathBlock23 : Array String := #[
  "third_party/blink/public/mojom/file_system_access/file_system_access_permission_mode.mojom",
  "third_party/blink/public/mojom/file_system_access/file_system_access_transfer_token.mojom",
  "third_party/blink/public/mojom/filesystem/file_system.mojom",
  "third_party/blink/public/mojom/fingerprinting_protection/noise_token.mojom",
  "third_party/blink/public/mojom/font_access/font_access.mojom",
  "third_party/blink/public/mojom/font_unique_name_lookup/font_unique_name_lookup.mojom",
  "third_party/blink/public/mojom/forms/form_control_type.mojom",
  "third_party/blink/public/mojom/frame/agent_cluster_key.mojom",
  "third_party/blink/public/mojom/frame/back_forward_cache_controller.mojom",
  "third_party/blink/public/mojom/frame/blocked_navigation_types.mojom",
  "third_party/blink/public/mojom/frame/color_scheme.mojom",
  "third_party/blink/public/mojom/frame/deferred_fetch_policy.mojom",
  "third_party/blink/public/mojom/frame/find_in_page.mojom",
  "third_party/blink/public/mojom/frame/frame.mojom",
  "third_party/blink/public/mojom/frame/frame_owner_properties.mojom",
  "third_party/blink/public/mojom/frame/frame_policy.mojom",
  "third_party/blink/public/mojom/frame/frame_replication_state.mojom",
  "third_party/blink/public/mojom/frame/frame_visual_properties.mojom",
  "third_party/blink/public/mojom/frame/fullscreen.mojom",
  "third_party/blink/public/mojom/frame/intrinsic_sizing_info.mojom",
  "third_party/blink/public/mojom/frame/lifecycle.mojom",
  "third_party/blink/public/mojom/frame/media_player_action.mojom",
  "third_party/blink/public/mojom/frame/policy_container.mojom",
  "third_party/blink/public/mojom/frame/remote_frame.mojom",
  "third_party/blink/public/mojom/frame/reporting_observer.mojom",
  "third_party/blink/public/mojom/frame/sudden_termination_disabler_type.mojom",
  "third_party/blink/public/mojom/frame/tree_scope_type.mojom",
  "third_party/blink/public/mojom/frame/triggering_event_info.mojom",
  "third_party/blink/public/mojom/frame/user_activation_notification_type.mojom",
  "third_party/blink/public/mojom/frame/user_activation_update_types.mojom",
  "third_party/blink/public/mojom/frame/view_transition_state.mojom",
  "third_party/blink/public/mojom/frame/viewport_intersection_state.mojom",
  "third_party/blink/public/mojom/frame_sinks/embedded_frame_sink.mojom",
  "third_party/blink/public/mojom/geolocation/geolocation_service.mojom",
  "third_party/blink/public/mojom/gpu/gpu.mojom",
  "third_party/blink/public/mojom/handwriting/handwriting.mojom",
  "third_party/blink/public/mojom/hid/hid.mojom",
  "third_party/blink/public/mojom/hyphenation/hyphenation.mojom",
  "third_party/blink/public/mojom/idle/idle_manager.mojom",
  "third_party/blink/public/mojom/image_downloader/image_downloader.mojom",
  "third_party/blink/public/mojom/image_replacement/image_replacement.mojom",
  "third_party/blink/public/mojom/indexeddb/indexeddb.mojom",
  "third_party/blink/public/mojom/input/focus_type.mojom",
  "third_party/blink/public/mojom/input/gesture_event.mojom",
  "third_party/blink/public/mojom/input/handwriting_gesture_result.mojom",
  "third_party/blink/public/mojom/input/ime_host.mojom",
  "third_party/blink/public/mojom/input/input_event.mojom",
  "third_party/blink/public/mojom/input/input_event_result.mojom",
  "third_party/blink/public/mojom/input/input_handler.mojom",
  "third_party/blink/public/mojom/input/input_host.mojom",
  "third_party/blink/public/mojom/input/input_messages.mojom",
  "third_party/blink/public/mojom/input/pointer_lock_context.mojom",
  "third_party/blink/public/mojom/input/pointer_lock_result.mojom",
  "third_party/blink/public/mojom/input/scroll_direction.mojom",
  "third_party/blink/public/mojom/input/stylus_writing_gesture.mojom",
  "third_party/blink/public/mojom/input/synchronous_compositor.mojom",
  "third_party/blink/public/mojom/input/text_input_host.mojom",
  "third_party/blink/public/mojom/input/touch_event.mojom",
  "third_party/blink/public/mojom/installation/installation.mojom",
  "third_party/blink/public/mojom/installedapp/installed_app_provider.mojom",
  "third_party/blink/public/mojom/installedapp/related_application.mojom",
  "third_party/blink/public/mojom/keyboard_lock/keyboard_lock.mojom",
  "third_party/blink/public/mojom/lcp_critical_path_predictor/lcp_critical_path_predictor.mojom",
  "third_party/blink/public/mojom/leak_detector/leak_detector.mojom"
]
def pathBlock24 : Array String := #[
  "third_party/blink/public/mojom/link_to_text/link_to_text.mojom",
  "third_party/blink/public/mojom/loader/code_cache.mojom",
  "third_party/blink/public/mojom/loader/content_security_notifier.mojom",
  "third_party/blink/public/mojom/loader/fetch_client_settings_object.mojom",
  "third_party/blink/public/mojom/loader/fetch_later.mojom",
  "third_party/blink/public/mojom/loader/javascript_framework_detection.mojom",
  "third_party/blink/public/mojom/loader/keep_alive_handle.mojom",
  "third_party/blink/public/mojom/loader/keep_alive_handle_factory.mojom",
  "third_party/blink/public/mojom/loader/local_resource_loader_config.mojom",
  "third_party/blink/public/mojom/loader/mhtml_load_result.mojom",
  "third_party/blink/public/mojom/loader/mixed_content.mojom",
  "third_party/blink/public/mojom/loader/navigation_predictor.mojom",
  "third_party/blink/public/mojom/loader/pause_subresource_loading_handle.mojom",
  "third_party/blink/public/mojom/loader/referrer.mojom",
  "third_party/blink/public/mojom/loader/request_context_frame_type.mojom",
  "third_party/blink/public/mojom/loader/resource_load_info.mojom",
  "third_party/blink/public/mojom/loader/resource_load_info_notifier.mojom",
  "third_party/blink/public/mojom/loader/same_document_navigation_type.mojom",
  "third_party/blink/public/mojom/loader/transferrable_url_loader.mojom",
  "third_party/blink/public/mojom/loader/url_loader_factory_bundle.mojom",
  "third_party/blink/public/mojom/lock_screen/lock_screen.mojom",
  "third_party/blink/public/mojom/locks/lock_manager.mojom",
  "third_party/blink/public/mojom/manifest/application_context.mojom",
  "third_party/blink/public/mojom/manifest/display_mode.mojom",
  "third_party/blink/public/mojom/manifest/manifest.mojom",
  "third_party/blink/public/mojom/manifest/manifest_launch_handler.mojom",
  "third_party/blink/public/mojom/manifest/manifest_manager.mojom",
  "third_party/blink/public/mojom/manifest/manifest_migration_behavior.mojom",
  "third_party/blink/public/mojom/manifest/manifest_observer.mojom",
  "third_party/blink/public/mojom/media/capture_handle_config.mojom",
  "third_party/blink/public/mojom/media/fullscreen_video_element.mojom",
  "third_party/blink/public/mojom/media/renderer_audio_input_stream_factory.mojom",
  "third_party/blink/public/mojom/media/renderer_audio_output_stream_factory.mojom",
  "third_party/blink/public/mojom/mediasession/media_session.mojom",
  "third_party/blink/public/mojom/mediastream/aec_dump.mojom",
  "third_party/blink/public/mojom/mediastream/media_devices.mojom",
  "third_party/blink/public/mojom/mediastream/media_stream.mojom",
  "third_party/blink/public/mojom/memory_usage_monitor_linux.mojom",
  "third_party/blink/public/mojom/messaging/cloneable_message.mojom",
  "third_party/blink/public/mojom/messaging/delegated_capability.mojom",
  "third_party/blink/public/mojom/messaging/message_port_descriptor.mojom",
  "third_party/blink/public/mojom/messaging/static_bitmap_image.mojom",
  "third_party/blink/public/mojom/messaging/task_attribution_id.mojom",
  "third_party/blink/public/mojom/messaging/transferable_message.mojom",
  "third_party/blink/public/mojom/messaging/user_activation_snapshot.mojom",
  "third_party/blink/public/mojom/mime/mime_registry.mojom",
  "third_party/blink/public/mojom/navigation/navigation_api_history_entry_arrays.mojom",
  "third_party/blink/public/mojom/navigation/navigation_params.mojom",
  "third_party/blink/public/mojom/navigation/navigation_policy.mojom",
  "third_party/blink/public/mojom/navigation/navigation_type_for_navigation_api.mojom",
  "third_party/blink/public/mojom/navigation/prefetched_signed_exchange_info.mojom",
  "third_party/blink/public/mojom/navigation/renderer_content_settings.mojom",
  "third_party/blink/public/mojom/navigation/renderer_eviction_reason.mojom",
  "third_party/blink/public/mojom/navigation/was_activated_option.mojom",
  "third_party/blink/public/mojom/notifications/notification.mojom",
  "third_party/blink/public/mojom/notifications/notification_service.mojom",
  "third_party/blink/public/mojom/on_device_translation/translation_manager.mojom",
  "third_party/blink/public/mojom/on_device_translation/translator.mojom",
  "third_party/blink/public/mojom/oom_intervention/oom_intervention.mojom",
  "third_party/blink/public/mojom/opengraph/metadata.mojom",
  "third_party/blink/public/mojom/origin_trials/origin_trial_state_host.mojom",
  "third_party/blink/public/mojom/origin_trials/origin_trials_settings.mojom",
  "third_party/blink/public/mojom/page/display_cutout.mojom",
  "third_party/blink/public/mojom/page/draggable_region.mojom"
]
def pathBlock25 : Array String := #[
  "third_party/blink/public/mojom/page/page.mojom",
  "third_party/blink/public/mojom/page/page_visibility_state.mojom",
  "third_party/blink/public/mojom/page/prerender_page_param.mojom",
  "third_party/blink/public/mojom/page/widget.mojom",
  "third_party/blink/public/mojom/page_state/page_state.mojom",
  "third_party/blink/public/mojom/payments/payment_app.mojom",
  "third_party/blink/public/mojom/payments/payment_app_events.mojom",
  "third_party/blink/public/mojom/payments/payment_handler_host.mojom",
  "third_party/blink/public/mojom/payments/payment_request.mojom",
  "third_party/blink/public/mojom/payments/secure_payment_confirmation_service.mojom",
  "third_party/blink/public/mojom/peerconnection/peer_connection_tracker.mojom",
  "third_party/blink/public/mojom/peerconnection/webrtc_ip_handling_policy.mojom",
  "third_party/blink/public/mojom/peerconnection/webrtc_ip_handling_url_entry.mojom",
  "third_party/blink/public/mojom/performance_manager/v8_detailed_memory_reporter.mojom",
  "third_party/blink/public/mojom/permissions/permission.mojom",
  "third_party/blink/public/mojom/permissions/permission_status.mojom",
  "third_party/blink/public/mojom/permissions_policy/document_policy_feature.mojom",
  "third_party/blink/public/mojom/permissions_policy/policy_disposition.mojom",
  "third_party/blink/public/mojom/permissions_policy/policy_value.mojom",
  "third_party/blink/public/mojom/persistent_renderer_prefs.mojom",
  "third_party/blink/public/mojom/picture_in_picture/picture_in_picture.mojom",
  "third_party/blink/public/mojom/picture_in_picture_window_options/picture_in_picture_window_options.mojom",
  "third_party/blink/public/mojom/plugins/plugin_registry.mojom",
  "third_party/blink/public/mojom/preloading/anchor_element_interaction_host.mojom",
  "third_party/blink/public/mojom/prerender/prerender.mojom",
  "third_party/blink/public/mojom/presentation/presentation.mojom",
  "third_party/blink/public/mojom/printing/web_printing.mojom",
  "third_party/blink/public/mojom/push_messaging/push_messaging.mojom",
  "third_party/blink/public/mojom/push_messaging/push_messaging_status.mojom",
  "third_party/blink/public/mojom/quota/quota_manager_host.mojom",
  "third_party/blink/public/mojom/quota/quota_types.mojom",
  "third_party/blink/public/mojom/remote_objects/remote_objects.mojom",
  "third_party/blink/public/mojom/render_accessibility.mojom",
  "third_party/blink/public/mojom/renderer_preference_watcher.mojom",
  "third_party/blink/public/mojom/renderer_preferences.mojom",
  "third_party/blink/public/mojom/reporting/reporting.mojom",
  "third_party/blink/public/mojom/safe_url_pattern.mojom",
  "third_party/blink/public/mojom/scheduler/web_scheduler_tracked_feature.mojom",
  "third_party/blink/public/mojom/script/script_evaluation_params.mojom",
  "third_party/blink/public/mojom/script/script_type.mojom",
  "third_party/blink/public/mojom/script_source_location.mojom",
  "third_party/blink/public/mojom/scroll/scroll_enums.mojom",
  "third_party/blink/public/mojom/scroll/scroll_into_view_params.mojom",
  "third_party/blink/public/mojom/scroll/scrollbar_mode.mojom",
  "third_party/blink/public/mojom/security_context/insecure_request_policy.mojom",
  "third_party/blink/public/mojom/security_context/outside_context_csp_violation_reporter.mojom",
  "third_party/blink/public/mojom/selection_menu/selection_menu_behavior.mojom",
  "third_party/blink/public/mojom/sensor/web_sensor_provider.mojom",
  "third_party/blink/public/mojom/serial/serial.mojom",
  "third_party/blink/public/mojom/service_worker/controller_service_worker.mojom",
  "third_party/blink/public/mojom/service_worker/controller_service_worker_mode.mojom",
  "third_party/blink/public/mojom/service_worker/dispatch_fetch_event_params.mojom",
  "third_party/blink/public/mojom/service_worker/embedded_worker.mojom",
  "third_party/blink/public/mojom/service_worker/navigation_preload_state.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_ancestor_frame_type.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_client.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_container.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_container_type.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_database.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_embedded_worker_status.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_error_type.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_event_status.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_fetch_handler_bypass_option.mojom"
]
def pathBlock26 : Array String := #[
  "third_party/blink/public/mojom/service_worker/service_worker_fetch_handler_type.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_fetch_response_callback.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_installed_scripts_manager.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_object.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_provider.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_registration.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_registration_options.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_router_rule.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_running_status_callback.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_state.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_stream_handle.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_worker_client.mojom",
  "third_party/blink/public/mojom/service_worker/service_worker_worker_client_registry.mojom",
  "third_party/blink/public/mojom/set_shape/set_shape.mojom",
  "third_party/blink/public/mojom/site_engagement/site_engagement.mojom",
  "third_party/blink/public/mojom/smart_card/smart_card.mojom",
  "third_party/blink/public/mojom/sms/webotp_service.mojom",
  "third_party/blink/public/mojom/speculation_rules/speculation_rules.mojom",
  "third_party/blink/public/mojom/speech/speech_synthesis.mojom",
  "third_party/blink/public/mojom/storage_access/storage_access_handle.mojom",
  "third_party/blink/public/mojom/storage_key/ancestor_chain_bit.mojom",
  "third_party/blink/public/mojom/storage_key/storage_key.mojom",
  "third_party/blink/public/mojom/subapps/sub_apps_service.mojom",
  "third_party/blink/public/mojom/timing/declarative_performance_observer.mojom",
  "third_party/blink/public/mojom/timing/performance_mark_or_measure.mojom",
  "third_party/blink/public/mojom/timing/resource_timing.mojom",
  "third_party/blink/public/mojom/tokens/tokens.mojom",
  "third_party/blink/public/mojom/unbounded_element/unbounded_element.mojom",
  "third_party/blink/public/mojom/unhandled_tap_notifier/unhandled_tap_notifier.mojom",
  "third_party/blink/public/mojom/usb/web_usb_service.mojom",
  "third_party/blink/public/mojom/use_counter/metrics/css_property_id.mojom",
  "third_party/blink/public/mojom/use_counter/metrics/web_feature.mojom",
  "third_party/blink/public/mojom/use_counter/metrics/webdx_feature.mojom",
  "third_party/blink/public/mojom/use_counter/use_counter_feature.mojom",
  "third_party/blink/public/mojom/user_agent/user_agent_metadata.mojom",
  "third_party/blink/public/mojom/v8_cache_options.mojom",
  "third_party/blink/public/mojom/wake_lock/wake_lock.mojom",
  "third_party/blink/public/mojom/web_install/web_install.mojom",
  "third_party/blink/public/mojom/web_launch/web_launch.mojom",
  "third_party/blink/public/mojom/webaudio/audio_context_manager.mojom",
  "third_party/blink/public/mojom/webauthn/authenticator.mojom",
  "third_party/blink/public/mojom/webid/digital_identity_request.mojom",
  "third_party/blink/public/mojom/webid/email_verification_request.mojom",
  "third_party/blink/public/mojom/webid/fedcm_identity_request.mojom",
  "third_party/blink/public/mojom/webid/federated_request.mojom",
  "third_party/blink/public/mojom/webnn/webnn_introspection.mojom",
  "third_party/blink/public/mojom/webpreferences/web_preferences.mojom",
  "third_party/blink/public/mojom/webrtc/rtc_logging.mojom",
  "third_party/blink/public/mojom/webshare/share_error.mojom",
  "third_party/blink/public/mojom/webshare/webshare.mojom",
  "third_party/blink/public/mojom/websockets/websocket_connector.mojom",
  "third_party/blink/public/mojom/webtransport/web_transport_connector.mojom",
  "third_party/blink/public/mojom/webview/webview_media_integrity.mojom",
  "third_party/blink/public/mojom/widget/device_emulation_params.mojom",
  "third_party/blink/public/mojom/widget/platform_widget.mojom",
  "third_party/blink/public/mojom/widget/record_content_to_visible_time_request.mojom",
  "third_party/blink/public/mojom/widget/visual_properties.mojom",
  "third_party/blink/public/mojom/window_features/window_features.mojom",
  "third_party/blink/public/mojom/worker/dedicated_worker_host.mojom",
  "third_party/blink/public/mojom/worker/dedicated_worker_host_factory.mojom",
  "third_party/blink/public/mojom/worker/shared_worker.mojom",
  "third_party/blink/public/mojom/worker/shared_worker_client.mojom",
  "third_party/blink/public/mojom/worker/shared_worker_connector.mojom",
  "third_party/blink/public/mojom/worker/shared_worker_creation_context_type.mojom"
]
def pathBlock27 : Array String := #[
  "third_party/blink/public/mojom/worker/shared_worker_exception_details.mojom",
  "third_party/blink/public/mojom/worker/shared_worker_factory.mojom",
  "third_party/blink/public/mojom/worker/shared_worker_host.mojom",
  "third_party/blink/public/mojom/worker/shared_worker_info.mojom",
  "third_party/blink/public/mojom/worker/subresource_loader_updater.mojom",
  "third_party/blink/public/mojom/worker/worker_content_settings_proxy.mojom",
  "third_party/blink/public/mojom/worker/worker_main_script_load_params.mojom",
  "third_party/blink/public/mojom/worker/worker_options.mojom",
  "third_party/blink/public/mojom/worker/worklet_global_scope_creation_params.mojom",
  "ui/accessibility/ax_constants.mojom",
  "ui/accessibility/ax_enums.mojom",
  "ui/accessibility/ax_features.mojom",
  "ui/accessibility/mojom/ax_action_data.mojom",
  "ui/accessibility/mojom/ax_assistant_structure.mojom",
  "ui/accessibility/mojom/ax_event.mojom",
  "ui/accessibility/mojom/ax_event_intent.mojom",
  "ui/accessibility/mojom/ax_location_and_scroll_updates.mojom",
  "ui/accessibility/mojom/ax_mode.mojom",
  "ui/accessibility/mojom/ax_node_data.mojom",
  "ui/accessibility/mojom/ax_relative_bounds.mojom",
  "ui/accessibility/mojom/ax_tree_checks.mojom",
  "ui/accessibility/mojom/ax_tree_data.mojom",
  "ui/accessibility/mojom/ax_tree_id.mojom",
  "ui/accessibility/mojom/ax_tree_update.mojom",
  "ui/accessibility/mojom/ax_updates_and_events.mojom",
  "ui/base/accelerators/mojom/accelerator.mojom",
  "ui/base/cursor/mojom/cursor.mojom",
  "ui/base/cursor/mojom/cursor_type.mojom",
  "ui/base/dragdrop/mojom/drag_drop_types.mojom",
  "ui/base/ime/mojom/ime_mojom_traits_test.mojom",
  "ui/base/ime/mojom/ime_types.mojom",
  "ui/base/ime/mojom/text_edit_commands.mojom",
  "ui/base/ime/mojom/text_input_state.mojom",
  "ui/base/ime/mojom/virtual_keyboard_types.mojom",
  "ui/base/mojom/attributed_string.mojom",
  "ui/base/mojom/color_mode.mojom",
  "ui/base/mojom/dialog_button.mojom",
  "ui/base/mojom/menu_source_type.mojom",
  "ui/base/mojom/themes.mojom",
  "ui/base/mojom/ui_base_types.mojom",
  "ui/base/mojom/window_open_disposition.mojom",
  "ui/base/mojom/window_show_state.mojom",
  "ui/color/color_id.mojom",
  "ui/color/scheme_variant.mojom",
  "ui/display/mojom/display.mojom",
  "ui/display/mojom/display_color_management.mojom",
  "ui/display/mojom/display_configuration_params.mojom",
  "ui/display/mojom/display_constants.mojom",
  "ui/display/mojom/display_layout.mojom",
  "ui/display/mojom/display_mode.mojom",
  "ui/display/mojom/display_snapshot.mojom",
  "ui/display/mojom/gamma_ramp_rgb_entry.mojom",
  "ui/display/mojom/screen_info.mojom",
  "ui/display/mojom/screen_infos.mojom",
  "ui/display/mojom/screen_orientation.mojom",
  "ui/events/ash/mojom/extended_fkeys_modifier.mojom",
  "ui/events/ash/mojom/meta_key.mojom",
  "ui/events/ash/mojom/modifier_key.mojom",
  "ui/events/ash/mojom/simulate_right_click_modifier.mojom",
  "ui/events/ash/mojom/six_pack_shortcut_modifier.mojom",
  "ui/events/mojom/event.mojom",
  "ui/events/mojom/event_constants.mojom",
  "ui/events/mojom/event_latency_metadata.mojom",
  "ui/events/mojom/keyboard_codes.mojom"
]
def pathBlock28 : Array String := #[
  "ui/events/mojom/motion_event_android.mojom",
  "ui/events/mojom/scroll_granularity.mojom",
  "ui/gfx/geometry/mojom/geometry.mojom",
  "ui/gfx/image/mojom/image.mojom",
  "ui/gfx/image/mojom/image_traits_test_service.mojom",
  "ui/gfx/mojom/accelerated_widget.mojom",
  "ui/gfx/mojom/buffer_types.mojom",
  "ui/gfx/mojom/ca_layer_params.mojom",
  "ui/gfx/mojom/ca_layer_result.mojom",
  "ui/gfx/mojom/color_space.mojom",
  "ui/gfx/mojom/delegated_ink_metadata.mojom",
  "ui/gfx/mojom/delegated_ink_point.mojom",
  "ui/gfx/mojom/delegated_ink_point_renderer.mojom",
  "ui/gfx/mojom/display_color_spaces.mojom",
  "ui/gfx/mojom/dxgi_info.mojom",
  "ui/gfx/mojom/font_render_params.mojom",
  "ui/gfx/mojom/frame_data.mojom",
  "ui/gfx/mojom/gpu_extra_info.mojom",
  "ui/gfx/mojom/gpu_fence_handle.mojom",
  "ui/gfx/mojom/hdr_metadata.mojom",
  "ui/gfx/mojom/hdr_static_metadata.mojom",
  "ui/gfx/mojom/linear_gradient.mojom",
  "ui/gfx/mojom/mask_filter_info.mojom",
  "ui/gfx/mojom/native_handle_types.mojom",
  "ui/gfx/mojom/overlay_priority_hint.mojom",
  "ui/gfx/mojom/overlay_transform.mojom",
  "ui/gfx/mojom/overlay_type.mojom",
  "ui/gfx/mojom/presentation_feedback.mojom",
  "ui/gfx/mojom/rrect_f.mojom",
  "ui/gfx/mojom/selection_bound.mojom",
  "ui/gfx/mojom/swap_result.mojom",
  "ui/gfx/mojom/swap_timings.mojom",
  "ui/gfx/mojom/traits_test_service.mojom",
  "ui/gfx/mojom/transform.mojom",
  "ui/gfx/range/mojom/range.mojom",
  "ui/gfx/range/mojom/range_traits_test_service.mojom",
  "ui/gl/mojom/gl_implementation.mojom",
  "ui/gl/mojom/gpu_preference.mojom",
  "ui/gl/mojom/traits_test_service.mojom",
  "ui/latency/mojom/latency_info.mojom",
  "ui/ozone/platform/drm/mojom/device_cursor.mojom",
  "ui/ozone/platform/drm/mojom/drm_device.mojom",
  "ui/ozone/platform/flatland/mojom/scenic_gpu_host.mojom",
  "ui/ozone/platform/flatland/mojom/scenic_gpu_service.mojom",
  "ui/ozone/platform/wayland/mojom/wayland_buffer_manager.mojom",
  "ui/ozone/platform/wayland/mojom/wayland_overlay_config.mojom",
  "ui/ozone/platform/wayland/mojom/wayland_overlay_config_traits_test_service.mojom",
  "ui/ozone/platform/wayland/mojom/wayland_presentation_info.mojom",
  "ui/ozone/public/mojom/gesture_properties_service.mojom",
  "ui/webui/examples/browser/ui/web/browser.mojom",
  "ui/webui/resources/cr_components/app_management/app_management.mojom",
  "ui/webui/resources/cr_components/color_change_listener/color_change_listener.mojom",
  "ui/webui/resources/cr_components/composebox/composebox.mojom",
  "ui/webui/resources/cr_components/customize_color_scheme_mode/customize_color_scheme_mode.mojom",
  "ui/webui/resources/cr_components/help_bubble/custom_help_bubble.mojom",
  "ui/webui/resources/cr_components/help_bubble/help_bubble.mojom",
  "ui/webui/resources/cr_components/history/foreign_sessions.mojom",
  "ui/webui/resources/cr_components/history/history.mojom",
  "ui/webui/resources/cr_components/history/history_cross_device_signin_promo.mojom",
  "ui/webui/resources/cr_components/history_clusters/history_clusters.mojom",
  "ui/webui/resources/cr_components/most_visited/most_visited.mojom",
  "ui/webui/resources/cr_components/search/plural_string_provider.mojom",
  "ui/webui/resources/cr_components/signin/signin.mojom",
  "ui/webui/resources/cr_components/theme_color_picker/theme_color_picker.mojom"
]
def pathBlock29 : Array String := #[
  "ui/webui/resources/js/batch_upload_promo/batch_upload_promo.mojom",
  "ui/webui/resources/js/browser_command/browser_command.mojom",
  "ui/webui/resources/js/metrics_reporter/metrics_reporter.mojom",
  "ui/webui/resources/js/tracked_element/tracked_element.mojom",
  "url/mojom/origin.mojom",
  "url/mojom/scheme_host_port.mojom",
  "url/mojom/url.mojom",
  "url/mojom/url_test.mojom"
]
def nodePaths : Array String := pathBlock0 ++ pathBlock1 ++ pathBlock2 ++ pathBlock3 ++ pathBlock4 ++ pathBlock5 ++ pathBlock6 ++ pathBlock7 ++ pathBlock8 ++ pathBlock9 ++ pathBlock10 ++ pathBlock11 ++ pathBlock12 ++ pathBlock13 ++ pathBlock14 ++ pathBlock15 ++ pathBlock16 ++ pathBlock17 ++ pathBlock18 ++ pathBlock19 ++ pathBlock20 ++ pathBlock21 ++ pathBlock22 ++ pathBlock23 ++ pathBlock24 ++ pathBlock25 ++ pathBlock26 ++ pathBlock27 ++ pathBlock28 ++ pathBlock29
def edgeBlock0 : List (Fin 1864 × Fin 1864) := [
  (⟨0, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨0, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨0, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨0, by decide +kernel⟩, ⟨1576, by decide +kernel⟩),
  (⟨0, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨0, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨0, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨5, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨5, by decide +kernel⟩, ⟨1753, by decide +kernel⟩),
  (⟨8, by decide +kernel⟩, ⟨3, by decide +kernel⟩),
  (⟨8, by decide +kernel⟩, ⟨6, by decide +kernel⟩),
  (⟨8, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨8, by decide +kernel⟩, ⟨1783, by decide +kernel⟩),
  (⟨8, by decide +kernel⟩, ⟨1784, by decide +kernel⟩),
  (⟨8, by decide +kernel⟩, ⟨1785, by decide +kernel⟩),
  (⟨8, by decide +kernel⟩, ⟨1786, by decide +kernel⟩),
  (⟨8, by decide +kernel⟩, ⟨1787, by decide +kernel⟩),
  (⟨12, by decide +kernel⟩, ⟨13, by decide +kernel⟩),
  (⟨14, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨15, by decide +kernel⟩, ⟨535, by decide +kernel⟩),
  (⟨15, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨15, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨15, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨15, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨16, by decide +kernel⟩, ⟨17, by decide +kernel⟩),
  (⟨16, by decide +kernel⟩, ⟨18, by decide +kernel⟩),
  (⟨16, by decide +kernel⟩, ⟨19, by decide +kernel⟩),
  (⟨16, by decide +kernel⟩, ⟨20, by decide +kernel⟩),
  (⟨16, by decide +kernel⟩, ⟨379, by decide +kernel⟩),
  (⟨16, by decide +kernel⟩, ⟨518, by decide +kernel⟩),
  (⟨16, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨16, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨16, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨17, by decide +kernel⟩, ⟨20, by decide +kernel⟩),
  (⟨18, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨19, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨21, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨22, by decide +kernel⟩, ⟨3, by decide +kernel⟩),
  (⟨22, by decide +kernel⟩, ⟨5, by decide +kernel⟩),
  (⟨22, by decide +kernel⟩, ⟨1784, by decide +kernel⟩),
  (⟨24, by decide +kernel⟩, ⟨25, by decide +kernel⟩),
  (⟨24, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨24, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨24, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨26, by decide +kernel⟩, ⟨8, by decide +kernel⟩),
  (⟨29, by decide +kernel⟩, ⟨11, by decide +kernel⟩),
  (⟨31, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨33, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨36, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨36, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨37, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨37, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨40, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨41, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨42, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨43, by decide +kernel⟩, ⟨1473, by decide +kernel⟩),
  (⟨43, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨44, by decide +kernel⟩, ⟨356, by decide +kernel⟩),
  (⟨44, by decide +kernel⟩, ⟨357, by decide +kernel⟩),
  (⟨44, by decide +kernel⟩, ⟨998, by decide +kernel⟩),
  (⟨44, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨44, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨45, by decide +kernel⟩, ⟨964, by decide +kernel⟩)
]
def edgeBlock1 : List (Fin 1864 × Fin 1864) := [
  (⟨45, by decide +kernel⟩, ⟨990, by decide +kernel⟩),
  (⟨45, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨45, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨46, by decide +kernel⟩, ⟨10, by decide +kernel⟩),
  (⟨46, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨46, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨46, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨46, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨46, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨46, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨47, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨48, by decide +kernel⟩, ⟨49, by decide +kernel⟩),
  (⟨48, by decide +kernel⟩, ⟨990, by decide +kernel⟩),
  (⟨48, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨48, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨50, by decide +kernel⟩, ⟨526, by decide +kernel⟩),
  (⟨50, by decide +kernel⟩, ⟨631, by decide +kernel⟩),
  (⟨50, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨50, by decide +kernel⟩, ⟨998, by decide +kernel⟩),
  (⟨50, by decide +kernel⟩, ⟨1233, by decide +kernel⟩),
  (⟨50, by decide +kernel⟩, ⟨1234, by decide +kernel⟩),
  (⟨52, by decide +kernel⟩, ⟨51, by decide +kernel⟩),
  (⟨53, by decide +kernel⟩, ⟨51, by decide +kernel⟩),
  (⟨54, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨55, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨56, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨56, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨56, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨59, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨60, by decide +kernel⟩, ⟨5, by decide +kernel⟩),
  (⟨60, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨61, by decide +kernel⟩, ⟨4, by decide +kernel⟩),
  (⟨61, by decide +kernel⟩, ⟨5, by decide +kernel⟩),
  (⟨61, by decide +kernel⟩, ⟨6, by decide +kernel⟩),
  (⟨61, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨61, by decide +kernel⟩, ⟨1753, by decide +kernel⟩),
  (⟨61, by decide +kernel⟩, ⟨1784, by decide +kernel⟩),
  (⟨63, by decide +kernel⟩, ⟨64, by decide +kernel⟩),
  (⟨64, by decide +kernel⟩, ⟨1319, by decide +kernel⟩),
  (⟨69, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨69, by decide +kernel⟩, ⟨1821, by decide +kernel⟩),
  (⟨75, by decide +kernel⟩, ⟨77, by decide +kernel⟩),
  (⟨75, by decide +kernel⟩, ⟨1318, by decide +kernel⟩),
  (⟨75, by decide +kernel⟩, ⟨1325, by decide +kernel⟩),
  (⟨75, by decide +kernel⟩, ⟨1335, by decide +kernel⟩),
  (⟨75, by decide +kernel⟩, ⟨1338, by decide +kernel⟩),
  (⟨75, by decide +kernel⟩, ⟨1367, by decide +kernel⟩),
  (⟨75, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨79, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨83, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨83, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨83, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨86, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨87, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨88, by decide +kernel⟩, ⟨645, by decide +kernel⟩),
  (⟨88, by decide +kernel⟩, ⟨987, by decide +kernel⟩),
  (⟨88, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨88, by decide +kernel⟩, ⟨998, by decide +kernel⟩),
  (⟨88, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨89, by decide +kernel⟩, ⟨91, by decide +kernel⟩),
  (⟨89, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨89, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨89, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨90, by decide +kernel⟩, ⟨565, by decide +kernel⟩)
]
def edgeBlock2 : List (Fin 1864 × Fin 1864) := [
  (⟨90, by decide +kernel⟩, ⟨567, by decide +kernel⟩),
  (⟨90, by decide +kernel⟩, ⟨970, by decide +kernel⟩),
  (⟨90, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨92, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨93, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨93, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨95, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨128, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨256, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨261, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨586, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨961, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨987, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨1000, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨1420, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨94, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨96, by decide +kernel⟩, ⟨261, by decide +kernel⟩),
  (⟨96, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨96, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨98, by decide +kernel⟩, ⟨94, by decide +kernel⟩),
  (⟨98, by decide +kernel⟩, ⟨261, by decide +kernel⟩),
  (⟨98, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨98, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨98, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨100, by decide +kernel⟩, ⟨123, by decide +kernel⟩),
  (⟨100, by decide +kernel⟩, ⟨975, by decide +kernel⟩),
  (⟨100, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨100, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨100, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨101, by decide +kernel⟩, ⟨107, by decide +kernel⟩),
  (⟨101, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨102, by decide +kernel⟩, ⟨101, by decide +kernel⟩),
  (⟨102, by decide +kernel⟩, ⟨105, by decide +kernel⟩),
  (⟨102, by decide +kernel⟩, ⟨106, by decide +kernel⟩),
  (⟨102, by decide +kernel⟩, ⟨108, by decide +kernel⟩),
  (⟨102, by decide +kernel⟩, ⟨109, by decide +kernel⟩),
  (⟨102, by decide +kernel⟩, ⟨965, by decide +kernel⟩),
  (⟨102, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨102, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨102, by decide +kernel⟩, ⟨1768, by decide +kernel⟩),
  (⟨102, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨104, by decide +kernel⟩, ⟨106, by decide +kernel⟩),
  (⟨104, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨105, by decide +kernel⟩, ⟨101, by decide +kernel⟩),
  (⟨108, by decide +kernel⟩, ⟨101, by decide +kernel⟩),
  (⟨108, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨108, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨108, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨110, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨111, by decide +kernel⟩, ⟨112, by decide +kernel⟩),
  (⟨112, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨113, by decide +kernel⟩, ⟨112, by decide +kernel⟩),
  (⟨114, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨114, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨115, by decide +kernel⟩, ⟨114, by decide +kernel⟩)
]
def edgeBlock3 : List (Fin 1864 × Fin 1864) := [
  (⟨116, by decide +kernel⟩, ⟨114, by decide +kernel⟩),
  (⟨117, by decide +kernel⟩, ⟨118, by decide +kernel⟩),
  (⟨117, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨118, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨118, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨119, by decide +kernel⟩, ⟨727, by decide +kernel⟩),
  (⟨119, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨124, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨125, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨126, by decide +kernel⟩, ⟨623, by decide +kernel⟩),
  (⟨127, by decide +kernel⟩, ⟨128, by decide +kernel⟩),
  (⟨127, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨127, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨127, by decide +kernel⟩, ⟨1447, by decide +kernel⟩),
  (⟨127, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨127, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨128, by decide +kernel⟩, ⟨969, by decide +kernel⟩),
  (⟨128, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨128, by decide +kernel⟩, ⟨1447, by decide +kernel⟩),
  (⟨128, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨129, by decide +kernel⟩, ⟨253, by decide +kernel⟩),
  (⟨129, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨132, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨132, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨134, by decide +kernel⟩, ⟨85, by decide +kernel⟩),
  (⟨135, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨136, by decide +kernel⟩, ⟨350, by decide +kernel⟩),
  (⟨136, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨136, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨137, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨141, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨141, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨142, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨143, by decide +kernel⟩, ⟨142, by decide +kernel⟩),
  (⟨143, by decide +kernel⟩, ⟨144, by decide +kernel⟩),
  (⟨143, by decide +kernel⟩, ⟨145, by decide +kernel⟩),
  (⟨143, by decide +kernel⟩, ⟨146, by decide +kernel⟩),
  (⟨144, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨148, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨148, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨150, by decide +kernel⟩, ⟨1842, by decide +kernel⟩),
  (⟨154, by decide +kernel⟩, ⟨3, by decide +kernel⟩),
  (⟨154, by decide +kernel⟩, ⟨8, by decide +kernel⟩),
  (⟨154, by decide +kernel⟩, ⟨1784, by decide +kernel⟩),
  (⟨155, by decide +kernel⟩, ⟨348, by decide +kernel⟩),
  (⟨158, by decide +kernel⟩, ⟨1842, by decide +kernel⟩),
  (⟨160, by decide +kernel⟩, ⟨57, by decide +kernel⟩),
  (⟨160, by decide +kernel⟩, ⟨58, by decide +kernel⟩),
  (⟨160, by decide +kernel⟩, ⟨161, by decide +kernel⟩),
  (⟨160, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨162, by decide +kernel⟩, ⟨58, by decide +kernel⟩),
  (⟨164, by decide +kernel⟩, ⟨796, by decide +kernel⟩),
  (⟨166, by decide +kernel⟩, ⟨584, by decide +kernel⟩),
  (⟨166, by decide +kernel⟩, ⟨586, by decide +kernel⟩),
  (⟨167, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨167, by decide +kernel⟩, ⟨998, by decide +kernel⟩),
  (⟨167, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨167, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨169, by decide +kernel⟩, ⟨229, by decide +kernel⟩),
  (⟨170, by decide +kernel⟩, ⟨590, by decide +kernel⟩),
  (⟨170, by decide +kernel⟩, ⟨961, by decide +kernel⟩),
  (⟨170, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨172, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨173, by decide +kernel⟩, ⟨121, by decide +kernel⟩)
]
def edgeBlock4 : List (Fin 1864 × Fin 1864) := [
  (⟨173, by decide +kernel⟩, ⟨985, by decide +kernel⟩),
  (⟨173, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨173, by decide +kernel⟩, ⟨1241, by decide +kernel⟩),
  (⟨173, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨175, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨175, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨177, by decide +kernel⟩, ⟨125, by decide +kernel⟩),
  (⟨177, by decide +kernel⟩, ⟨987, by decide +kernel⟩),
  (⟨177, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨185, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨185, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨186, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨191, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨194, by decide +kernel⟩, ⟨969, by decide +kernel⟩),
  (⟨194, by decide +kernel⟩, ⟨970, by decide +kernel⟩),
  (⟨194, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨194, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨194, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨195, by decide +kernel⟩, ⟨1050, by decide +kernel⟩),
  (⟨196, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨197, by decide +kernel⟩, ⟨198, by decide +kernel⟩),
  (⟨197, by decide +kernel⟩, ⟨476, by decide +kernel⟩),
  (⟨197, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨197, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨199, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨199, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨200, by decide +kernel⟩, ⟨645, by decide +kernel⟩),
  (⟨200, by decide +kernel⟩, ⟨646, by decide +kernel⟩),
  (⟨200, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨200, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨202, by decide +kernel⟩, ⟨206, by decide +kernel⟩),
  (⟨202, by decide +kernel⟩, ⟨642, by decide +kernel⟩),
  (⟨202, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨202, by decide +kernel⟩, ⟨1852, by decide +kernel⟩),
  (⟨202, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨204, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨204, by decide +kernel⟩, ⟨1852, by decide +kernel⟩),
  (⟨207, by decide +kernel⟩, ⟨206, by decide +kernel⟩),
  (⟨207, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨209, by decide +kernel⟩, ⟨645, by decide +kernel⟩),
  (⟨209, by decide +kernel⟩, ⟨647, by decide +kernel⟩),
  (⟨209, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨209, by decide +kernel⟩, ⟨1765, by decide +kernel⟩),
  (⟨209, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨210, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨211, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨212, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨213, by decide +kernel⟩, ⟨645, by decide +kernel⟩),
  (⟨213, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨213, by decide +kernel⟩, ⟨1826, by decide +kernel⟩),
  (⟨214, by decide +kernel⟩, ⟨645, by decide +kernel⟩),
  (⟨214, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨214, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨215, by decide +kernel⟩, ⟨655, by decide +kernel⟩),
  (⟨215, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨215, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨215, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨215, by decide +kernel⟩, ⟨1233, by decide +kernel⟩),
  (⟨215, by decide +kernel⟩, ⟨1234, by decide +kernel⟩),
  (⟨215, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨217, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨219, by decide +kernel⟩, ⟨727, by decide +kernel⟩),
  (⟨219, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨220, by decide +kernel⟩, ⟨992, by decide +kernel⟩)
]
def edgeBlock5 : List (Fin 1864 × Fin 1864) := [
  (⟨221, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨221, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨224, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨226, by decide +kernel⟩, ⟨225, by decide +kernel⟩),
  (⟨226, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨226, by decide +kernel⟩, ⟨1826, by decide +kernel⟩),
  (⟨227, by decide +kernel⟩, ⟨1768, by decide +kernel⟩),
  (⟨227, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨229, by decide +kernel⟩, ⟨642, by decide +kernel⟩),
  (⟨229, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨229, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨229, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨230, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨231, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨231, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨231, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨232, by decide +kernel⟩, ⟨1768, by decide +kernel⟩),
  (⟨232, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨235, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨237, by decide +kernel⟩, ⟨718, by decide +kernel⟩),
  (⟨237, by decide +kernel⟩, ⟨719, by decide +kernel⟩),
  (⟨237, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨239, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨239, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨239, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨240, by decide +kernel⟩, ⟨727, by decide +kernel⟩),
  (⟨240, by decide +kernel⟩, ⟨728, by decide +kernel⟩),
  (⟨240, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨240, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨240, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨240, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨241, by decide +kernel⟩, ⟨557, by decide +kernel⟩),
  (⟨241, by decide +kernel⟩, ⟨728, by decide +kernel⟩),
  (⟨241, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨241, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨241, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨241, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨243, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨243, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨244, by decide +kernel⟩, ⟨317, by decide +kernel⟩),
  (⟨244, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨244, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨244, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨245, by decide +kernel⟩, ⟨1073, by decide +kernel⟩),
  (⟨245, by decide +kernel⟩, ⟨1075, by decide +kernel⟩),
  (⟨249, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨249, by decide +kernel⟩, ⟨1360, by decide +kernel⟩),
  (⟨250, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨250, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨251, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨252, by decide +kernel⟩, ⟨559, by decide +kernel⟩),
  (⟨252, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨252, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨252, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨254, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨255, by decide +kernel⟩, ⟨544, by decide +kernel⟩),
  (⟨255, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨255, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨255, by decide +kernel⟩, ⟨1419, by decide +kernel⟩),
  (⟨255, by decide +kernel⟩, ⟨1424, by decide +kernel⟩),
  (⟨255, by decide +kernel⟩, ⟨1525, by decide +kernel⟩),
  (⟨255, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨255, by decide +kernel⟩, ⟨1793, by decide +kernel⟩),
  (⟨255, by decide +kernel⟩, ⟨1794, by decide +kernel⟩)
]
def edgeBlock6 : List (Fin 1864 × Fin 1864) := [
  (⟨256, by decide +kernel⟩, ⟨261, by decide +kernel⟩),
  (⟨256, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨256, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨257, by decide +kernel⟩, ⟨255, by decide +kernel⟩),
  (⟨257, by decide +kernel⟩, ⟨544, by decide +kernel⟩),
  (⟨257, by decide +kernel⟩, ⟨613, by decide +kernel⟩),
  (⟨257, by decide +kernel⟩, ⟨659, by decide +kernel⟩),
  (⟨257, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨257, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨257, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨257, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨257, by decide +kernel⟩, ⟨1721, by decide +kernel⟩),
  (⟨257, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨257, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨258, by decide +kernel⟩, ⟨579, by decide +kernel⟩),
  (⟨263, by decide +kernel⟩, ⟨732, by decide +kernel⟩),
  (⟨263, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨263, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨263, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨264, by decide +kernel⟩, ⟨965, by decide +kernel⟩),
  (⟨264, by decide +kernel⟩, ⟨1512, by decide +kernel⟩),
  (⟨264, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨264, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨265, by decide +kernel⟩, ⟨297, by decide +kernel⟩),
  (⟨265, by decide +kernel⟩, ⟨628, by decide +kernel⟩),
  (⟨265, by decide +kernel⟩, ⟨677, by decide +kernel⟩),
  (⟨265, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨265, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨265, by decide +kernel⟩, ⟨1795, by decide +kernel⟩),
  (⟨265, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨266, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨267, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨267, by decide +kernel⟩, ⟨1545, by decide +kernel⟩),
  (⟨267, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨270, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨273, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨275, by decide +kernel⟩, ⟨779, by decide +kernel⟩),
  (⟨275, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨275, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨275, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨275, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨276, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨276, by decide +kernel⟩, ⟨1751, by decide +kernel⟩),
  (⟨277, by decide +kernel⟩, ⟨965, by decide +kernel⟩),
  (⟨277, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨277, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨277, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨277, by decide +kernel⟩, ⟨1742, by decide +kernel⟩),
  (⟨277, by decide +kernel⟩, ⟨1750, by decide +kernel⟩),
  (⟨277, by decide +kernel⟩, ⟨1751, by decide +kernel⟩),
  (⟨277, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨278, by decide +kernel⟩, ⟨897, by decide +kernel⟩),
  (⟨278, by decide +kernel⟩, ⟨902, by decide +kernel⟩),
  (⟨278, by decide +kernel⟩, ⟨903, by decide +kernel⟩),
  (⟨278, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨278, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨278, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨278, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨278, by decide +kernel⟩, ⟨1739, by decide +kernel⟩),
  (⟨279, by decide +kernel⟩, ⟨583, by decide +kernel⟩),
  (⟨279, by decide +kernel⟩, ⟨584, by decide +kernel⟩),
  (⟨279, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨279, by decide +kernel⟩, ⟨1134, by decide +kernel⟩),
  (⟨279, by decide +kernel⟩, ⟨1862, by decide +kernel⟩)
]
def edgeBlock7 : List (Fin 1864 × Fin 1864) := [
  (⟨280, by decide +kernel⟩, ⟨1134, by decide +kernel⟩),
  (⟨281, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨281, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨281, by decide +kernel⟩, ⟨1134, by decide +kernel⟩),
  (⟨283, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨285, by decide +kernel⟩, ⟨998, by decide +kernel⟩),
  (⟨288, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨289, by decide +kernel⟩, ⟨290, by decide +kernel⟩),
  (⟨292, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨293, by decide +kernel⟩, ⟨294, by decide +kernel⟩),
  (⟨293, by decide +kernel⟩, ⟨295, by decide +kernel⟩),
  (⟨293, by decide +kernel⟩, ⟨296, by decide +kernel⟩),
  (⟨293, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨294, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨295, by decide +kernel⟩, ⟨291, by decide +kernel⟩),
  (⟨295, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨296, by decide +kernel⟩, ⟨689, by decide +kernel⟩),
  (⟨296, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨296, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨297, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨297, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨297, by decide +kernel⟩, ⟨1795, by decide +kernel⟩),
  (⟨297, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨298, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨300, by decide +kernel⟩, ⟨298, by decide +kernel⟩),
  (⟨300, by decide +kernel⟩, ⟨299, by decide +kernel⟩),
  (⟨300, by decide +kernel⟩, ⟨301, by decide +kernel⟩),
  (⟨300, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨300, by decide +kernel⟩, ⟨1243, by decide +kernel⟩),
  (⟨300, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨301, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨301, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨301, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨302, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨303, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨303, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨303, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨304, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨305, by decide +kernel⟩, ⟨304, by decide +kernel⟩),
  (⟨305, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨305, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨306, by decide +kernel⟩, ⟨304, by decide +kernel⟩),
  (⟨306, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨307, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨307, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨307, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨307, by decide +kernel⟩, ⟨1005, by decide +kernel⟩),
  (⟨307, by decide +kernel⟩, ⟨1006, by decide +kernel⟩),
  (⟨307, by decide +kernel⟩, ⟨1007, by decide +kernel⟩),
  (⟨307, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨307, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨308, by decide +kernel⟩, ⟨302, by decide +kernel⟩),
  (⟨308, by decide +kernel⟩, ⟨303, by decide +kernel⟩),
  (⟨308, by decide +kernel⟩, ⟨305, by decide +kernel⟩),
  (⟨308, by decide +kernel⟩, ⟨306, by decide +kernel⟩),
  (⟨308, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨309, by decide +kernel⟩, ⟨936, by decide +kernel⟩),
  (⟨309, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨309, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨310, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨310, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨311, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨311, by decide +kernel⟩, ⟨1002, by decide +kernel⟩),
  (⟨311, by decide +kernel⟩, ⟨1024, by decide +kernel⟩)
]
def edgeBlock8 : List (Fin 1864 × Fin 1864) := [
  (⟨311, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨312, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨312, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨312, by decide +kernel⟩, ⟨1795, by decide +kernel⟩),
  (⟨313, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨313, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨313, by decide +kernel⟩, ⟨1002, by decide +kernel⟩),
  (⟨313, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨317, by decide +kernel⟩, ⟨290, by decide +kernel⟩),
  (⟨317, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨317, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨319, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨320, by decide +kernel⟩, ⟨1576, by decide +kernel⟩),
  (⟨321, by decide +kernel⟩, ⟨342, by decide +kernel⟩),
  (⟨321, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨322, by decide +kernel⟩, ⟨320, by decide +kernel⟩),
  (⟨322, by decide +kernel⟩, ⟨340, by decide +kernel⟩),
  (⟨322, by decide +kernel⟩, ⟨731, by decide +kernel⟩),
  (⟨322, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨322, by decide +kernel⟩, ⟨1169, by decide +kernel⟩),
  (⟨322, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨323, by decide +kernel⟩, ⟨321, by decide +kernel⟩),
  (⟨323, by decide +kernel⟩, ⟨322, by decide +kernel⟩),
  (⟨323, by decide +kernel⟩, ⟨324, by decide +kernel⟩),
  (⟨323, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨323, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨324, by decide +kernel⟩, ⟨989, by decide +kernel⟩),
  (⟨324, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨328, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨330, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨331, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨335, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨336, by decide +kernel⟩, ⟨976, by decide +kernel⟩),
  (⟨337, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨339, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨339, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨339, by decide +kernel⟩, ⟨1817, by decide +kernel⟩),
  (⟨341, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨344, by decide +kernel⟩, ⟨345, by decide +kernel⟩),
  (⟨344, by decide +kernel⟩, ⟨347, by decide +kernel⟩),
  (⟨344, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨344, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨346, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨347, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨350, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨350, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨353, by decide +kernel⟩, ⟨355, by decide +kernel⟩),
  (⟨353, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨354, by decide +kernel⟩, ⟨353, by decide +kernel⟩),
  (⟨354, by decide +kernel⟩, ⟨355, by decide +kernel⟩),
  (⟨354, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨355, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨357, by decide +kernel⟩, ⟨356, by decide +kernel⟩),
  (⟨357, by decide +kernel⟩, ⟨528, by decide +kernel⟩),
  (⟨357, by decide +kernel⟩, ⟨998, by decide +kernel⟩),
  (⟨358, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨359, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨363, by decide +kernel⟩, ⟨361, by decide +kernel⟩),
  (⟨363, by decide +kernel⟩, ⟨362, by decide +kernel⟩),
  (⟨364, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨364, by decide +kernel⟩, ⟨972, by decide +kernel⟩),
  (⟨364, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨364, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨364, by decide +kernel⟩, ⟨1024, by decide +kernel⟩)
]
def edgeBlock9 : List (Fin 1864 × Fin 1864) := [
  (⟨367, by decide +kernel⟩, ⟨368, by decide +kernel⟩),
  (⟨367, by decide +kernel⟩, ⟨381, by decide +kernel⟩),
  (⟨367, by decide +kernel⟩, ⟨389, by decide +kernel⟩),
  (⟨367, by decide +kernel⟩, ⟨417, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨365, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨367, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨368, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨369, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨371, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨372, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨373, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨374, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨376, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨377, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨378, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨380, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨381, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨382, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨383, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨384, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨385, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨386, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨387, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨388, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨390, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨391, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨392, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨394, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨395, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨396, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨397, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨398, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨399, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨400, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨401, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨402, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨403, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨405, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨406, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨407, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨408, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨409, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨410, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨411, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨413, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨414, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨415, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨418, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨419, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨420, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨421, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨422, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨423, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨424, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨431, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨432, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨433, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨434, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨500, by decide +kernel⟩),
  (⟨370, by decide +kernel⟩, ⟨1025, by decide +kernel⟩),
  (⟨371, by decide +kernel⟩, ⟨404, by decide +kernel⟩),
  (⟨376, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨378, by decide +kernel⟩, ⟨887, by decide +kernel⟩),
  (⟨382, by decide +kernel⟩, ⟨995, by decide +kernel⟩)
]
def edgeBlock10 : List (Fin 1864 × Fin 1864) := [
  (⟨384, by decide +kernel⟩, ⟨592, by decide +kernel⟩),
  (⟨384, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨388, by decide +kernel⟩, ⟨367, by decide +kernel⟩),
  (⟨388, by decide +kernel⟩, ⟨375, by decide +kernel⟩),
  (⟨388, by decide +kernel⟩, ⟨389, by decide +kernel⟩),
  (⟨388, by decide +kernel⟩, ⟨393, by decide +kernel⟩),
  (⟨388, by decide +kernel⟩, ⟨425, by decide +kernel⟩),
  (⟨388, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨388, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨388, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨388, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨390, by decide +kernel⟩, ⟨505, by decide +kernel⟩),
  (⟨391, by decide +kernel⟩, ⟨389, by decide +kernel⟩),
  (⟨392, by decide +kernel⟩, ⟨389, by decide +kernel⟩),
  (⟨392, by decide +kernel⟩, ⟨391, by decide +kernel⟩),
  (⟨392, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨394, by decide +kernel⟩, ⟨367, by decide +kernel⟩),
  (⟨394, by decide +kernel⟩, ⟨375, by decide +kernel⟩),
  (⟨394, by decide +kernel⟩, ⟨379, by decide +kernel⟩),
  (⟨394, by decide +kernel⟩, ⟨393, by decide +kernel⟩),
  (⟨394, by decide +kernel⟩, ⟨417, by decide +kernel⟩),
  (⟨394, by decide +kernel⟩, ⟨990, by decide +kernel⟩),
  (⟨394, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨398, by decide +kernel⟩, ⟨1081, by decide +kernel⟩),
  (⟨400, by decide +kernel⟩, ⟨366, by decide +kernel⟩),
  (⟨400, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨402, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨403, by decide +kernel⟩, ⟨367, by decide +kernel⟩),
  (⟨403, by decide +kernel⟩, ⟨404, by decide +kernel⟩),
  (⟨403, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨403, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨405, by decide +kernel⟩, ⟨375, by decide +kernel⟩),
  (⟨405, by decide +kernel⟩, ⟨389, by decide +kernel⟩),
  (⟨408, by decide +kernel⟩, ⟨452, by decide +kernel⟩),
  (⟨408, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨410, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨411, by decide +kernel⟩, ⟨366, by decide +kernel⟩),
  (⟨413, by decide +kernel⟩, ⟨412, by decide +kernel⟩),
  (⟨414, by decide +kernel⟩, ⟨368, by decide +kernel⟩),
  (⟨414, by decide +kernel⟩, ⟨389, by decide +kernel⟩),
  (⟨415, by decide +kernel⟩, ⟨1241, by decide +kernel⟩),
  (⟨416, by decide +kernel⟩, ⟨948, by decide +kernel⟩),
  (⟨416, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨416, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨418, by decide +kernel⟩, ⟨389, by decide +kernel⟩),
  (⟨418, by decide +kernel⟩, ⟨425, by decide +kernel⟩),
  (⟨424, by decide +kernel⟩, ⟨416, by decide +kernel⟩),
  (⟨424, by decide +kernel⟩, ⟨426, by decide +kernel⟩),
  (⟨424, by decide +kernel⟩, ⟨427, by decide +kernel⟩),
  (⟨424, by decide +kernel⟩, ⟨428, by decide +kernel⟩),
  (⟨424, by decide +kernel⟩, ⟨430, by decide +kernel⟩),
  (⟨424, by decide +kernel⟩, ⟨493, by decide +kernel⟩),
  (⟨424, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨425, by decide +kernel⟩, ⟨389, by decide +kernel⟩),
  (⟨426, by decide +kernel⟩, ⟨389, by decide +kernel⟩),
  (⟨426, by decide +kernel⟩, ⟨425, by decide +kernel⟩),
  (⟨426, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨427, by decide +kernel⟩, ⟨389, by decide +kernel⟩),
  (⟨427, by decide +kernel⟩, ⟨425, by decide +kernel⟩),
  (⟨427, by decide +kernel⟩, ⟨429, by decide +kernel⟩),
  (⟨427, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨428, by decide +kernel⟩, ⟨389, by decide +kernel⟩),
  (⟨428, by decide +kernel⟩, ⟨425, by decide +kernel⟩),
  (⟨428, by decide +kernel⟩, ⟨1024, by decide +kernel⟩)
]
def edgeBlock11 : List (Fin 1864 × Fin 1864) := [
  (⟨429, by decide +kernel⟩, ⟨389, by decide +kernel⟩),
  (⟨429, by decide +kernel⟩, ⟨425, by decide +kernel⟩),
  (⟨430, by decide +kernel⟩, ⟨389, by decide +kernel⟩),
  (⟨430, by decide +kernel⟩, ⟨425, by decide +kernel⟩),
  (⟨430, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨431, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨436, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨436, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨437, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨438, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨439, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨441, by decide +kernel⟩, ⟨524, by decide +kernel⟩),
  (⟨441, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨441, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨443, by decide +kernel⟩, ⟨442, by decide +kernel⟩),
  (⟨443, by decide +kernel⟩, ⟨444, by decide +kernel⟩),
  (⟨443, by decide +kernel⟩, ⟨446, by decide +kernel⟩),
  (⟨443, by decide +kernel⟩, ⟨447, by decide +kernel⟩),
  (⟨443, by decide +kernel⟩, ⟨448, by decide +kernel⟩),
  (⟨443, by decide +kernel⟩, ⟨450, by decide +kernel⟩),
  (⟨443, by decide +kernel⟩, ⟨536, by decide +kernel⟩),
  (⟨443, by decide +kernel⟩, ⟨537, by decide +kernel⟩),
  (⟨445, by decide +kernel⟩, ⟨11, by decide +kernel⟩),
  (⟨446, by decide +kernel⟩, ⟨11, by decide +kernel⟩),
  (⟨446, by decide +kernel⟩, ⟨448, by decide +kernel⟩),
  (⟨446, by decide +kernel⟩, ⟨450, by decide +kernel⟩),
  (⟨446, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨448, by decide +kernel⟩, ⟨450, by decide +kernel⟩),
  (⟨448, by decide +kernel⟩, ⟨538, by decide +kernel⟩),
  (⟨449, by decide +kernel⟩, ⟨447, by decide +kernel⟩),
  (⟨449, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨449, by decide +kernel⟩, ⟨998, by decide +kernel⟩),
  (⟨452, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨453, by decide +kernel⟩, ⟨452, by decide +kernel⟩),
  (⟨454, by decide +kernel⟩, ⟨359, by decide +kernel⟩),
  (⟨454, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨457, by decide +kernel⟩, ⟨460, by decide +kernel⟩),
  (⟨457, by decide +kernel⟩, ⟨461, by decide +kernel⟩),
  (⟨457, by decide +kernel⟩, ⟨463, by decide +kernel⟩),
  (⟨458, by decide +kernel⟩, ⟨457, by decide +kernel⟩),
  (⟨458, by decide +kernel⟩, ⟨459, by decide +kernel⟩),
  (⟨458, by decide +kernel⟩, ⟨460, by decide +kernel⟩),
  (⟨458, by decide +kernel⟩, ⟨461, by decide +kernel⟩),
  (⟨458, by decide +kernel⟩, ⟨462, by decide +kernel⟩),
  (⟨458, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨458, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨458, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨460, by decide +kernel⟩, ⟨463, by decide +kernel⟩),
  (⟨461, by decide +kernel⟩, ⟨460, by decide +kernel⟩),
  (⟨461, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨462, by decide +kernel⟩, ⟨464, by decide +kernel⟩),
  (⟨462, by decide +kernel⟩, ⟨965, by decide +kernel⟩),
  (⟨466, by decide +kernel⟩, ⟨465, by decide +kernel⟩),
  (⟨467, by decide +kernel⟩, ⟨465, by decide +kernel⟩),
  (⟨468, by decide +kernel⟩, ⟨359, by decide +kernel⟩),
  (⟨468, by decide +kernel⟩, ⟨454, by decide +kernel⟩),
  (⟨469, by decide +kernel⟩, ⟨480, by decide +kernel⟩),
  (⟨471, by decide +kernel⟩, ⟨472, by decide +kernel⟩),
  (⟨471, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨472, by decide +kernel⟩, ⟨802, by decide +kernel⟩),
  (⟨472, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨472, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨473, by decide +kernel⟩, ⟨474, by decide +kernel⟩),
  (⟨474, by decide +kernel⟩, ⟨476, by decide +kernel⟩)
]
def edgeBlock12 : List (Fin 1864 × Fin 1864) := [
  (⟨474, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨475, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨477, by decide +kernel⟩, ⟨478, by decide +kernel⟩),
  (⟨477, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨479, by decide +kernel⟩, ⟨469, by decide +kernel⟩),
  (⟨479, by decide +kernel⟩, ⟨470, by decide +kernel⟩),
  (⟨479, by decide +kernel⟩, ⟨471, by decide +kernel⟩),
  (⟨479, by decide +kernel⟩, ⟨472, by decide +kernel⟩),
  (⟨479, by decide +kernel⟩, ⟨473, by decide +kernel⟩),
  (⟨479, by decide +kernel⟩, ⟨477, by decide +kernel⟩),
  (⟨479, by decide +kernel⟩, ⟨481, by decide +kernel⟩),
  (⟨479, by decide +kernel⟩, ⟨482, by decide +kernel⟩),
  (⟨479, by decide +kernel⟩, ⟨492, by decide +kernel⟩),
  (⟨479, by decide +kernel⟩, ⟨534, by decide +kernel⟩),
  (⟨479, by decide +kernel⟩, ⟨796, by decide +kernel⟩),
  (⟨479, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨481, by decide +kernel⟩, ⟨480, by decide +kernel⟩),
  (⟨481, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨481, by decide +kernel⟩, ⟨1090, by decide +kernel⟩),
  (⟨481, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨481, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨481, by decide +kernel⟩, ⟨1148, by decide +kernel⟩),
  (⟨481, by decide +kernel⟩, ⟨1209, by decide +kernel⟩),
  (⟨482, by decide +kernel⟩, ⟨483, by decide +kernel⟩),
  (⟨482, by decide +kernel⟩, ⟨1147, by decide +kernel⟩),
  (⟨482, by decide +kernel⟩, ⟨1170, by decide +kernel⟩),
  (⟨482, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨484, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨484, by decide +kernel⟩, ⟨1826, by decide +kernel⟩),
  (⟨484, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨486, by decide +kernel⟩, ⟨485, by decide +kernel⟩),
  (⟨486, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨487, by decide +kernel⟩, ⟨905, by decide +kernel⟩),
  (⟨487, by decide +kernel⟩, ⟨965, by decide +kernel⟩),
  (⟨487, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨487, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨487, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨487, by decide +kernel⟩, ⟨1281, by decide +kernel⟩),
  (⟨487, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨487, by decide +kernel⟩, ⟨1328, by decide +kernel⟩),
  (⟨487, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨487, by decide +kernel⟩, ⟨1795, by decide +kernel⟩),
  (⟨489, by decide +kernel⟩, ⟨491, by decide +kernel⟩),
  (⟨490, by decide +kernel⟩, ⟨359, by decide +kernel⟩),
  (⟨490, by decide +kernel⟩, ⟨489, by decide +kernel⟩),
  (⟨490, by decide +kernel⟩, ⟨491, by decide +kernel⟩),
  (⟨490, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨491, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨493, by decide +kernel⟩, ⟨494, by decide +kernel⟩),
  (⟨493, by decide +kernel⟩, ⟨496, by decide +kernel⟩),
  (⟨493, by decide +kernel⟩, ⟨497, by decide +kernel⟩),
  (⟨493, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨493, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨494, by decide +kernel⟩, ⟨407, by decide +kernel⟩),
  (⟨494, by decide +kernel⟩, ⟨416, by decide +kernel⟩),
  (⟨494, by decide +kernel⟩, ⟨495, by decide +kernel⟩),
  (⟨494, by decide +kernel⟩, ⟨496, by decide +kernel⟩),
  (⟨494, by decide +kernel⟩, ⟨497, by decide +kernel⟩),
  (⟨498, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨499, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨499, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨499, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨499, by decide +kernel⟩, ⟨1243, by decide +kernel⟩),
  (⟨499, by decide +kernel⟩, ⟨1751, by decide +kernel⟩)
]
def edgeBlock13 : List (Fin 1864 × Fin 1864) := [
  (⟨500, by decide +kernel⟩, ⟨501, by decide +kernel⟩),
  (⟨501, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨502, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨502, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨502, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨503, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨503, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨504, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨505, by decide +kernel⟩, ⟨506, by decide +kernel⟩),
  (⟨512, by decide +kernel⟩, ⟨448, by decide +kernel⟩),
  (⟨517, by decide +kernel⟩, ⟨518, by decide +kernel⟩),
  (⟨517, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨517, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨517, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨520, by decide +kernel⟩, ⟨527, by decide +kernel⟩),
  (⟨521, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨522, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨523, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨523, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨524, by decide +kernel⟩, ⟨517, by decide +kernel⟩),
  (⟨524, by decide +kernel⟩, ⟨519, by decide +kernel⟩),
  (⟨524, by decide +kernel⟩, ⟨521, by decide +kernel⟩),
  (⟨524, by decide +kernel⟩, ⟨522, by decide +kernel⟩),
  (⟨524, by decide +kernel⟩, ⟨523, by decide +kernel⟩),
  (⟨524, by decide +kernel⟩, ⟨525, by decide +kernel⟩),
  (⟨524, by decide +kernel⟩, ⟨526, by decide +kernel⟩),
  (⟨524, by decide +kernel⟩, ⟨528, by decide +kernel⟩),
  (⟨524, by decide +kernel⟩, ⟨529, by decide +kernel⟩),
  (⟨524, by decide +kernel⟩, ⟨530, by decide +kernel⟩),
  (⟨525, by decide +kernel⟩, ⟨520, by decide +kernel⟩),
  (⟨526, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨528, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨530, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨530, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨532, by decide +kernel⟩, ⟨531, by decide +kernel⟩),
  (⟨532, by decide +kernel⟩, ⟨1273, by decide +kernel⟩),
  (⟨534, by decide +kernel⟩, ⟨535, by decide +kernel⟩),
  (⟨534, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨534, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨534, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨536, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨537, by decide +kernel⟩, ⟨538, by decide +kernel⟩),
  (⟨538, by decide +kernel⟩, ⟨535, by decide +kernel⟩),
  (⟨538, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨539, by decide +kernel⟩, ⟨905, by decide +kernel⟩),
  (⟨539, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨539, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨543, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨544, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨545, by decide +kernel⟩, ⟨550, by decide +kernel⟩),
  (⟨545, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨546, by decide +kernel⟩, ⟨550, by decide +kernel⟩),
  (⟨546, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨546, by decide +kernel⟩, ⟨993, by decide +kernel⟩),
  (⟨546, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨546, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨546, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨549, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨549, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨550, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨550, by decide +kernel⟩, ⟨993, by decide +kernel⟩),
  (⟨550, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨550, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨550, by decide +kernel⟩, ⟨1794, by decide +kernel⟩)
]
def edgeBlock14 : List (Fin 1864 × Fin 1864) := [
  (⟨550, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨551, by decide +kernel⟩, ⟨550, by decide +kernel⟩),
  (⟨552, by decide +kernel⟩, ⟨969, by decide +kernel⟩),
  (⟨552, by decide +kernel⟩, ⟨970, by decide +kernel⟩),
  (⟨552, by decide +kernel⟩, ⟨998, by decide +kernel⟩),
  (⟨552, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨553, by decide +kernel⟩, ⟨554, by decide +kernel⟩),
  (⟨553, by decide +kernel⟩, ⟨969, by decide +kernel⟩),
  (⟨553, by decide +kernel⟩, ⟨970, by decide +kernel⟩),
  (⟨553, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨553, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨555, by decide +kernel⟩, ⟨559, by decide +kernel⟩),
  (⟨555, by decide +kernel⟩, ⟨969, by decide +kernel⟩),
  (⟨555, by decide +kernel⟩, ⟨970, by decide +kernel⟩),
  (⟨555, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨556, by decide +kernel⟩, ⟨557, by decide +kernel⟩),
  (⟨556, by decide +kernel⟩, ⟨558, by decide +kernel⟩),
  (⟨556, by decide +kernel⟩, ⟨559, by decide +kernel⟩),
  (⟨556, by decide +kernel⟩, ⟨969, by decide +kernel⟩),
  (⟨556, by decide +kernel⟩, ⟨970, by decide +kernel⟩),
  (⟨556, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨557, by decide +kernel⟩, ⟨559, by decide +kernel⟩),
  (⟨557, by decide +kernel⟩, ⟨727, by decide +kernel⟩),
  (⟨557, by decide +kernel⟩, ⟨728, by decide +kernel⟩),
  (⟨557, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨557, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨558, by decide +kernel⟩, ⟨557, by decide +kernel⟩),
  (⟨558, by decide +kernel⟩, ⟨559, by decide +kernel⟩),
  (⟨560, by decide +kernel⟩, ⟨557, by decide +kernel⟩),
  (⟨560, by decide +kernel⟩, ⟨559, by decide +kernel⟩),
  (⟨560, by decide +kernel⟩, ⟨969, by decide +kernel⟩),
  (⟨560, by decide +kernel⟩, ⟨970, by decide +kernel⟩),
  (⟨560, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨561, by decide +kernel⟩, ⟨559, by decide +kernel⟩),
  (⟨561, by decide +kernel⟩, ⟨969, by decide +kernel⟩),
  (⟨561, by decide +kernel⟩, ⟨970, by decide +kernel⟩),
  (⟨561, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨562, by decide +kernel⟩, ⟨552, by decide +kernel⟩),
  (⟨562, by decide +kernel⟩, ⟨969, by decide +kernel⟩),
  (⟨562, by decide +kernel⟩, ⟨970, by decide +kernel⟩),
  (⟨562, by decide +kernel⟩, ⟨1765, by decide +kernel⟩),
  (⟨562, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨563, by decide +kernel⟩, ⟨564, by decide +kernel⟩),
  (⟨563, by decide +kernel⟩, ⟨565, by decide +kernel⟩),
  (⟨563, by decide +kernel⟩, ⟨567, by decide +kernel⟩),
  (⟨563, by decide +kernel⟩, ⟨1765, by decide +kernel⟩),
  (⟨564, by decide +kernel⟩, ⟨565, by decide +kernel⟩),
  (⟨564, by decide +kernel⟩, ⟨969, by decide +kernel⟩),
  (⟨564, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨565, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨566, by decide +kernel⟩, ⟨564, by decide +kernel⟩),
  (⟨566, by decide +kernel⟩, ⟨565, by decide +kernel⟩),
  (⟨566, by decide +kernel⟩, ⟨567, by decide +kernel⟩),
  (⟨566, by decide +kernel⟩, ⟨586, by decide +kernel⟩),
  (⟨566, by decide +kernel⟩, ⟨969, by decide +kernel⟩),
  (⟨566, by decide +kernel⟩, ⟨970, by decide +kernel⟩),
  (⟨566, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨566, by decide +kernel⟩, ⟨1756, by decide +kernel⟩),
  (⟨566, by decide +kernel⟩, ⟨1765, by decide +kernel⟩),
  (⟨566, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨566, by decide +kernel⟩, ⟨1859, by decide +kernel⟩),
  (⟨566, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨567, by decide +kernel⟩, ⟨554, by decide +kernel⟩),
  (⟨567, by decide +kernel⟩, ⟨564, by decide +kernel⟩)
]
def edgeBlock15 : List (Fin 1864 × Fin 1864) := [
  (⟨567, by decide +kernel⟩, ⟨565, by decide +kernel⟩),
  (⟨567, by decide +kernel⟩, ⟨586, by decide +kernel⟩),
  (⟨567, by decide +kernel⟩, ⟨969, by decide +kernel⟩),
  (⟨567, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨567, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨567, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨567, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨567, by decide +kernel⟩, ⟨1826, by decide +kernel⟩),
  (⟨567, by decide +kernel⟩, ⟨1859, by decide +kernel⟩),
  (⟨568, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨569, by decide +kernel⟩, ⟨937, by decide +kernel⟩),
  (⟨570, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨571, by decide +kernel⟩, ⟨570, by decide +kernel⟩),
  (⟨571, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨572, by decide +kernel⟩, ⟨570, by decide +kernel⟩),
  (⟨572, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨572, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨572, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨573, by decide +kernel⟩, ⟨577, by decide +kernel⟩),
  (⟨573, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨574, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨576, by decide +kernel⟩, ⟨577, by decide +kernel⟩),
  (⟨576, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨577, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨578, by decide +kernel⟩, ⟨577, by decide +kernel⟩),
  (⟨578, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨578, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨578, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨580, by decide +kernel⟩, ⟨581, by decide +kernel⟩),
  (⟨581, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨581, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨582, by decide +kernel⟩, ⟨584, by decide +kernel⟩),
  (⟨583, by decide +kernel⟩, ⟨584, by decide +kernel⟩),
  (⟨583, by decide +kernel⟩, ⟨586, by decide +kernel⟩),
  (⟨583, by decide +kernel⟩, ⟨1196, by decide +kernel⟩),
  (⟨583, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨583, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨584, by decide +kernel⟩, ⟨585, by decide +kernel⟩),
  (⟨584, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨584, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨587, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨587, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨588, by decide +kernel⟩, ⟨589, by decide +kernel⟩),
  (⟨588, by decide +kernel⟩, ⟨590, by decide +kernel⟩),
  (⟨588, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨590, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨590, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨591, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨591, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨591, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨591, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨592, by decide +kernel⟩, ⟨665, by decide +kernel⟩),
  (⟨592, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨593, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨595, by decide +kernel⟩, ⟨596, by decide +kernel⟩),
  (⟨598, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨598, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨599, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨601, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨601, by decide +kernel⟩, ⟨1084, by decide +kernel⟩),
  (⟨601, by decide +kernel⟩, ⟨1795, by decide +kernel⟩),
  (⟨602, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨602, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨602, by decide +kernel⟩, ⟨1690, by decide +kernel⟩)
]
def edgeBlock16 : List (Fin 1864 × Fin 1864) := [
  (⟨603, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨603, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨603, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨604, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨606, by decide +kernel⟩, ⟨605, by decide +kernel⟩),
  (⟨606, by decide +kernel⟩, ⟨626, by decide +kernel⟩),
  (⟨608, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨608, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨609, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨609, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨609, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨609, by decide +kernel⟩, ⟨1519, by decide +kernel⟩),
  (⟨609, by decide +kernel⟩, ⟨1520, by decide +kernel⟩),
  (⟨609, by decide +kernel⟩, ⟨1718, by decide +kernel⟩),
  (⟨609, by decide +kernel⟩, ⟨1792, by decide +kernel⟩),
  (⟨609, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨611, by decide +kernel⟩, ⟨610, by decide +kernel⟩),
  (⟨611, by decide +kernel⟩, ⟨656, by decide +kernel⟩),
  (⟨611, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨611, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨611, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨611, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨611, by decide +kernel⟩, ⟨1576, by decide +kernel⟩),
  (⟨612, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨613, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨613, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨614, by decide +kernel⟩, ⟨777, by decide +kernel⟩),
  (⟨615, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨615, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨615, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨615, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨615, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨616, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨618, by decide +kernel⟩, ⟨622, by decide +kernel⟩),
  (⟨618, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨620, by decide +kernel⟩, ⟨616, by decide +kernel⟩),
  (⟨620, by decide +kernel⟩, ⟨617, by decide +kernel⟩),
  (⟨620, by decide +kernel⟩, ⟨618, by decide +kernel⟩),
  (⟨620, by decide +kernel⟩, ⟨619, by decide +kernel⟩),
  (⟨620, by decide +kernel⟩, ⟨622, by decide +kernel⟩),
  (⟨620, by decide +kernel⟩, ⟨623, by decide +kernel⟩),
  (⟨620, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨620, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨620, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨620, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨620, by decide +kernel⟩, ⟨1625, by decide +kernel⟩),
  (⟨620, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨620, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨621, by decide +kernel⟩, ⟨620, by decide +kernel⟩),
  (⟨622, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨622, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨622, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨626, by decide +kernel⟩, ⟨629, by decide +kernel⟩),
  (⟨626, by decide +kernel⟩, ⟨987, by decide +kernel⟩),
  (⟨626, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨627, by decide +kernel⟩, ⟨626, by decide +kernel⟩),
  (⟨628, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨628, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨631, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨633, by decide +kernel⟩, ⟨632, by decide +kernel⟩),
  (⟨633, by decide +kernel⟩, ⟨634, by decide +kernel⟩),
  (⟨633, by decide +kernel⟩, ⟨635, by decide +kernel⟩),
  (⟨633, by decide +kernel⟩, ⟨636, by decide +kernel⟩),
  (⟨633, by decide +kernel⟩, ⟨999, by decide +kernel⟩)
]
def edgeBlock17 : List (Fin 1864 × Fin 1864) := [
  (⟨633, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨633, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨633, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨634, by decide +kernel⟩, ⟨878, by decide +kernel⟩),
  (⟨634, by decide +kernel⟩, ⟨897, by decide +kernel⟩),
  (⟨634, by decide +kernel⟩, ⟨900, by decide +kernel⟩),
  (⟨634, by decide +kernel⟩, ⟨903, by decide +kernel⟩),
  (⟨634, by decide +kernel⟩, ⟨935, by decide +kernel⟩),
  (⟨634, by decide +kernel⟩, ⟨955, by decide +kernel⟩),
  (⟨634, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨634, by decide +kernel⟩, ⟨1199, by decide +kernel⟩),
  (⟨634, by decide +kernel⟩, ⟨1342, by decide +kernel⟩),
  (⟨636, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨636, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨637, by decide +kernel⟩, ⟨1861, by decide +kernel⟩),
  (⟨640, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨643, by decide +kernel⟩, ⟨647, by decide +kernel⟩),
  (⟨645, by decide +kernel⟩, ⟨643, by decide +kernel⟩),
  (⟨645, by decide +kernel⟩, ⟨644, by decide +kernel⟩),
  (⟨645, by decide +kernel⟩, ⟨646, by decide +kernel⟩),
  (⟨645, by decide +kernel⟩, ⟨647, by decide +kernel⟩),
  (⟨645, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨645, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨645, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨645, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨645, by decide +kernel⟩, ⟨1768, by decide +kernel⟩),
  (⟨645, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨645, by decide +kernel⟩, ⟨1826, by decide +kernel⟩),
  (⟨645, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨646, by decide +kernel⟩, ⟨643, by decide +kernel⟩),
  (⟨646, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨646, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨648, by decide +kernel⟩, ⟨649, by decide +kernel⟩),
  (⟨648, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨648, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨648, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨648, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨650, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨651, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨653, by decide +kernel⟩, ⟨652, by decide +kernel⟩),
  (⟨653, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨654, by decide +kernel⟩, ⟨987, by decide +kernel⟩),
  (⟨654, by decide +kernel⟩, ⟨1232, by decide +kernel⟩),
  (⟨654, by decide +kernel⟩, ⟨1233, by decide +kernel⟩),
  (⟨655, by decide +kernel⟩, ⟨654, by decide +kernel⟩),
  (⟨655, by decide +kernel⟩, ⟨987, by decide +kernel⟩),
  (⟨655, by decide +kernel⟩, ⟨1232, by decide +kernel⟩),
  (⟨655, by decide +kernel⟩, ⟨1233, by decide +kernel⟩),
  (⟨658, by decide +kernel⟩, ⟨657, by decide +kernel⟩),
  (⟨658, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨659, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨660, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨661, by decide +kernel⟩, ⟨967, by decide +kernel⟩),
  (⟨661, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨661, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨661, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨661, by decide +kernel⟩, ⟨1182, by decide +kernel⟩),
  (⟨661, by decide +kernel⟩, ⟨1541, by decide +kernel⟩),
  (⟨661, by decide +kernel⟩, ⟨1585, by decide +kernel⟩),
  (⟨661, by decide +kernel⟩, ⟨1697, by decide +kernel⟩),
  (⟨661, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨662, by decide +kernel⟩, ⟨663, by decide +kernel⟩),
  (⟨662, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨662, by decide +kernel⟩, ⟨971, by decide +kernel⟩)
]
def edgeBlock18 : List (Fin 1864 × Fin 1864) := [
  (⟨662, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨662, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨662, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨662, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨663, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨663, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨664, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨664, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨666, by decide +kernel⟩, ⟨667, by decide +kernel⟩),
  (⟨666, by decide +kernel⟩, ⟨668, by decide +kernel⟩),
  (⟨666, by decide +kernel⟩, ⟨669, by decide +kernel⟩),
  (⟨666, by decide +kernel⟩, ⟨985, by decide +kernel⟩),
  (⟨666, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨666, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨666, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨668, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨669, by decide +kernel⟩, ⟨967, by decide +kernel⟩),
  (⟨670, by decide +kernel⟩, ⟨722, by decide +kernel⟩),
  (⟨671, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨672, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨672, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨672, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨672, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨672, by decide +kernel⟩, ⟨1006, by decide +kernel⟩),
  (⟨672, by decide +kernel⟩, ⟨1751, by decide +kernel⟩),
  (⟨672, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨673, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨676, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨677, by decide +kernel⟩, ⟨676, by decide +kernel⟩),
  (⟨677, by decide +kernel⟩, ⟨680, by decide +kernel⟩),
  (⟨677, by decide +kernel⟩, ⟨681, by decide +kernel⟩),
  (⟨677, by decide +kernel⟩, ⟨683, by decide +kernel⟩),
  (⟨677, by decide +kernel⟩, ⟨726, by decide +kernel⟩),
  (⟨679, by decide +kernel⟩, ⟨678, by decide +kernel⟩),
  (⟨679, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨679, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨679, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨679, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨679, by decide +kernel⟩, ⟨1795, by decide +kernel⟩),
  (⟨680, by decide +kernel⟩, ⟨679, by decide +kernel⟩),
  (⟨680, by decide +kernel⟩, ⟨682, by decide +kernel⟩),
  (⟨680, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨680, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨680, by decide +kernel⟩, ⟨1229, by decide +kernel⟩),
  (⟨680, by decide +kernel⟩, ⟨1754, by decide +kernel⟩),
  (⟨680, by decide +kernel⟩, ⟨1763, by decide +kernel⟩),
  (⟨680, by decide +kernel⟩, ⟨1767, by decide +kernel⟩),
  (⟨680, by decide +kernel⟩, ⟨1789, by decide +kernel⟩),
  (⟨680, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨680, by decide +kernel⟩, ⟨1795, by decide +kernel⟩),
  (⟨680, by decide +kernel⟩, ⟨1799, by decide +kernel⟩),
  (⟨681, by decide +kernel⟩, ⟨985, by decide +kernel⟩),
  (⟨681, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨681, by decide +kernel⟩, ⟨1753, by decide +kernel⟩),
  (⟨681, by decide +kernel⟩, ⟨1764, by decide +kernel⟩),
  (⟨681, by decide +kernel⟩, ⟨1768, by decide +kernel⟩),
  (⟨681, by decide +kernel⟩, ⟨1772, by decide +kernel⟩),
  (⟨681, by decide +kernel⟩, ⟨1788, by decide +kernel⟩),
  (⟨681, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨681, by decide +kernel⟩, ⟨1799, by decide +kernel⟩),
  (⟨682, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨682, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨683, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨683, by decide +kernel⟩, ⟨1759, by decide +kernel⟩)
]
def edgeBlock19 : List (Fin 1864 × Fin 1864) := [
  (⟨683, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨683, by decide +kernel⟩, ⟨1826, by decide +kernel⟩),
  (⟨684, by decide +kernel⟩, ⟨685, by decide +kernel⟩),
  (⟨684, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨684, by decide +kernel⟩, ⟨987, by decide +kernel⟩),
  (⟨684, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨684, by decide +kernel⟩, ⟨1134, by decide +kernel⟩),
  (⟨684, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨684, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨685, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨686, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨686, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨689, by decide +kernel⟩, ⟨690, by decide +kernel⟩),
  (⟨689, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨689, by decide +kernel⟩, ⟨972, by decide +kernel⟩),
  (⟨690, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨690, by decide +kernel⟩, ⟨990, by decide +kernel⟩),
  (⟨691, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨691, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨692, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨692, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨693, by decide +kernel⟩, ⟨593, by decide +kernel⟩),
  (⟨693, by decide +kernel⟩, ⟨663, by decide +kernel⟩),
  (⟨693, by decide +kernel⟩, ⟨987, by decide +kernel⟩),
  (⟨693, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨693, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨693, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨693, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨693, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨694, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨694, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨695, by decide +kernel⟩, ⟨599, by decide +kernel⟩),
  (⟨695, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨695, by decide +kernel⟩, ⟨1006, by decide +kernel⟩),
  (⟨695, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨695, by decide +kernel⟩, ⟨1751, by decide +kernel⟩),
  (⟨695, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨696, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨696, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨696, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨696, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨697, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨698, by decide +kernel⟩, ⟨697, by decide +kernel⟩),
  (⟨698, by decide +kernel⟩, ⟨699, by decide +kernel⟩),
  (⟨698, by decide +kernel⟩, ⟨700, by decide +kernel⟩),
  (⟨698, by decide +kernel⟩, ⟨702, by decide +kernel⟩),
  (⟨698, by decide +kernel⟩, ⟨704, by decide +kernel⟩),
  (⟨698, by decide +kernel⟩, ⟨713, by decide +kernel⟩),
  (⟨698, by decide +kernel⟩, ⟨715, by decide +kernel⟩),
  (⟨698, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨698, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨698, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨698, by decide +kernel⟩, ⟨1513, by decide +kernel⟩),
  (⟨698, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨699, by decide +kernel⟩, ⟨704, by decide +kernel⟩),
  (⟨699, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨699, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨700, by decide +kernel⟩, ⟨697, by decide +kernel⟩),
  (⟨700, by decide +kernel⟩, ⟨704, by decide +kernel⟩),
  (⟨700, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨700, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨700, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨700, by decide +kernel⟩, ⟨1186, by decide +kernel⟩),
  (⟨700, by decide +kernel⟩, ⟨1860, by decide +kernel⟩)
]
def edgeBlock20 : List (Fin 1864 × Fin 1864) := [
  (⟨701, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨701, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨701, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨701, by decide +kernel⟩, ⟨1396, by decide +kernel⟩),
  (⟨703, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨703, by decide +kernel⟩, ⟨1630, by decide +kernel⟩),
  (⟨703, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨704, by decide +kernel⟩, ⟨702, by decide +kernel⟩),
  (⟨704, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨705, by decide +kernel⟩, ⟨704, by decide +kernel⟩),
  (⟨705, by decide +kernel⟩, ⟨713, by decide +kernel⟩),
  (⟨705, by decide +kernel⟩, ⟨715, by decide +kernel⟩),
  (⟨705, by decide +kernel⟩, ⟨1113, by decide +kernel⟩),
  (⟨705, by decide +kernel⟩, ⟨1124, by decide +kernel⟩),
  (⟨705, by decide +kernel⟩, ⟨1406, by decide +kernel⟩),
  (⟨705, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨706, by decide +kernel⟩, ⟨1473, by decide +kernel⟩),
  (⟨706, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨707, by decide +kernel⟩, ⟨965, by decide +kernel⟩),
  (⟨707, by decide +kernel⟩, ⟨967, by decide +kernel⟩),
  (⟨707, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨707, by decide +kernel⟩, ⟨972, by decide +kernel⟩),
  (⟨707, by decide +kernel⟩, ⟨973, by decide +kernel⟩),
  (⟨707, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨708, by decide +kernel⟩, ⟨713, by decide +kernel⟩),
  (⟨708, by decide +kernel⟩, ⟨715, by decide +kernel⟩),
  (⟨708, by decide +kernel⟩, ⟨1450, by decide +kernel⟩),
  (⟨708, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨709, by decide +kernel⟩, ⟨704, by decide +kernel⟩),
  (⟨709, by decide +kernel⟩, ⟨1630, by decide +kernel⟩),
  (⟨709, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨710, by decide +kernel⟩, ⟨967, by decide +kernel⟩),
  (⟨710, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨710, by decide +kernel⟩, ⟨1113, by decide +kernel⟩),
  (⟨710, by decide +kernel⟩, ⟨1494, by decide +kernel⟩),
  (⟨710, by decide +kernel⟩, ⟨1639, by decide +kernel⟩),
  (⟨710, by decide +kernel⟩, ⟨1653, by decide +kernel⟩),
  (⟨710, by decide +kernel⟩, ⟨1655, by decide +kernel⟩),
  (⟨710, by decide +kernel⟩, ⟨1659, by decide +kernel⟩),
  (⟨710, by decide +kernel⟩, ⟨1664, by decide +kernel⟩),
  (⟨710, by decide +kernel⟩, ⟨1670, by decide +kernel⟩),
  (⟨710, by decide +kernel⟩, ⟨1671, by decide +kernel⟩),
  (⟨710, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨710, by decide +kernel⟩, ⟨1695, by decide +kernel⟩),
  (⟨710, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨711, by decide +kernel⟩, ⟨710, by decide +kernel⟩),
  (⟨711, by decide +kernel⟩, ⟨713, by decide +kernel⟩),
  (⟨711, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨711, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨711, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨711, by decide +kernel⟩, ⟨1129, by decide +kernel⟩),
  (⟨711, by decide +kernel⟩, ⟨1223, by decide +kernel⟩),
  (⟨711, by decide +kernel⟩, ⟨1664, by decide +kernel⟩),
  (⟨711, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨711, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨712, by decide +kernel⟩, ⟨1449, by decide +kernel⟩),
  (⟨712, by decide +kernel⟩, ⟨1450, by decide +kernel⟩),
  (⟨712, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨713, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨714, by decide +kernel⟩, ⟨707, by decide +kernel⟩),
  (⟨714, by decide +kernel⟩, ⟨708, by decide +kernel⟩),
  (⟨714, by decide +kernel⟩, ⟨712, by decide +kernel⟩),
  (⟨714, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨714, by decide +kernel⟩, ⟨1024, by decide +kernel⟩)
]
def edgeBlock21 : List (Fin 1864 × Fin 1864) := [
  (⟨715, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨715, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨716, by decide +kernel⟩, ⟨707, by decide +kernel⟩),
  (⟨716, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨716, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨716, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨717, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨718, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨718, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨720, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨720, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨721, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨722, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨722, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨723, by decide +kernel⟩, ⟨724, by decide +kernel⟩),
  (⟨723, by decide +kernel⟩, ⟨1375, by decide +kernel⟩),
  (⟨723, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨724, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨724, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨725, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨725, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨725, by decide +kernel⟩, ⟨1318, by decide +kernel⟩),
  (⟨725, by decide +kernel⟩, ⟨1489, by decide +kernel⟩),
  (⟨725, by decide +kernel⟩, ⟨1514, by decide +kernel⟩),
  (⟨726, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨726, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨726, by decide +kernel⟩, ⟨1084, by decide +kernel⟩),
  (⟨729, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨729, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨729, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨729, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨730, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨730, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨731, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨732, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨732, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨732, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨732, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨735, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨735, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨736, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨737, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨738, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨740, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨740, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨741, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨741, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨742, by decide +kernel⟩, ⟨741, by decide +kernel⟩),
  (⟨743, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨744, by decide +kernel⟩, ⟨697, by decide +kernel⟩),
  (⟨744, by decide +kernel⟩, ⟨700, by decide +kernel⟩),
  (⟨744, by decide +kernel⟩, ⟨702, by decide +kernel⟩),
  (⟨744, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨745, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨746, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨746, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨746, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨746, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨747, by decide +kernel⟩, ⟨807, by decide +kernel⟩),
  (⟨747, by decide +kernel⟩, ⟨809, by decide +kernel⟩),
  (⟨747, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨748, by decide +kernel⟩, ⟨749, by decide +kernel⟩),
  (⟨748, by decide +kernel⟩, ⟨754, by decide +kernel⟩),
  (⟨748, by decide +kernel⟩, ⟨1485, by decide +kernel⟩)
]
def edgeBlock22 : List (Fin 1864 × Fin 1864) := [
  (⟨748, by decide +kernel⟩, ⟨1488, by decide +kernel⟩),
  (⟨748, by decide +kernel⟩, ⟨1498, by decide +kernel⟩),
  (⟨748, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨748, by decide +kernel⟩, ⟨1736, by decide +kernel⟩),
  (⟨749, by decide +kernel⟩, ⟨1390, by decide +kernel⟩),
  (⟨749, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨750, by decide +kernel⟩, ⟨876, by decide +kernel⟩),
  (⟨750, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨750, by decide +kernel⟩, ⟨976, by decide +kernel⟩),
  (⟨750, by decide +kernel⟩, ⟨983, by decide +kernel⟩),
  (⟨750, by decide +kernel⟩, ⟨1259, by decide +kernel⟩),
  (⟨750, by decide +kernel⟩, ⟨1262, by decide +kernel⟩),
  (⟨752, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨752, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨752, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨66, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨755, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨762, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨772, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨775, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨780, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨875, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1105, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1218, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1219, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1220, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1222, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1223, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1246, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1301, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1329, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1390, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1398, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1404, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1414, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1438, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1456, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1486, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1487, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1488, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1492, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1494, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1495, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1498, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1549, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1551, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1555, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1579, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1583, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1584, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1600, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1602, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1603, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1621, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1634, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1649, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1657, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1710, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1718, by decide +kernel⟩)
]
def edgeBlock23 : List (Fin 1864 × Fin 1864) := [
  (⟨754, by decide +kernel⟩, ⟨1720, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1721, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1751, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1768, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1861, by decide +kernel⟩),
  (⟨754, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨755, by decide +kernel⟩, ⟨1246, by decide +kernel⟩),
  (⟨755, by decide +kernel⟩, ⟨1404, by decide +kernel⟩),
  (⟨756, by decide +kernel⟩, ⟨656, by decide +kernel⟩),
  (⟨756, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨757, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨757, by decide +kernel⟩, ⟨1793, by decide +kernel⟩),
  (⟨757, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨758, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨759, by decide +kernel⟩, ⟨760, by decide +kernel⟩),
  (⟨760, by decide +kernel⟩, ⟨761, by decide +kernel⟩),
  (⟨760, by decide +kernel⟩, ⟨982, by decide +kernel⟩),
  (⟨761, by decide +kernel⟩, ⟨982, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨755, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨773, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨998, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1174, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1183, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1218, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1220, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1223, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1414, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1450, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1494, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1537, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1540, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1549, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1553, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1554, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1555, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1583, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1616, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1618, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1644, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1649, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1657, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨762, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨763, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨763, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨764, by decide +kernel⟩, ⟨985, by decide +kernel⟩),
  (⟨764, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨764, by decide +kernel⟩, ⟨1411, by decide +kernel⟩),
  (⟨764, by decide +kernel⟩, ⟨1520, by decide +kernel⟩),
  (⟨764, by decide +kernel⟩, ⟨1712, by decide +kernel⟩),
  (⟨764, by decide +kernel⟩, ⟨1754, by decide +kernel⟩),
  (⟨764, by decide +kernel⟩, ⟨1758, by decide +kernel⟩),
  (⟨764, by decide +kernel⟩, ⟨1762, by decide +kernel⟩),
  (⟨764, by decide +kernel⟩, ⟨1781, by decide +kernel⟩),
  (⟨764, by decide +kernel⟩, ⟨1788, by decide +kernel⟩),
  (⟨764, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨764, by decide +kernel⟩, ⟨1799, by decide +kernel⟩)
]
def edgeBlock24 : List (Fin 1864 × Fin 1864) := [
  (⟨764, by decide +kernel⟩, ⟨1826, by decide +kernel⟩),
  (⟨764, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨765, by decide +kernel⟩, ⟨748, by decide +kernel⟩),
  (⟨765, by decide +kernel⟩, ⟨876, by decide +kernel⟩),
  (⟨765, by decide +kernel⟩, ⟨976, by decide +kernel⟩),
  (⟨765, by decide +kernel⟩, ⟨986, by decide +kernel⟩),
  (⟨765, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨765, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨765, by decide +kernel⟩, ⟨1153, by decide +kernel⟩),
  (⟨765, by decide +kernel⟩, ⟨1164, by decide +kernel⟩),
  (⟨765, by decide +kernel⟩, ⟨1404, by decide +kernel⟩),
  (⟨765, by decide +kernel⟩, ⟨1428, by decide +kernel⟩),
  (⟨765, by decide +kernel⟩, ⟨1597, by decide +kernel⟩),
  (⟨765, by decide +kernel⟩, ⟨1698, by decide +kernel⟩),
  (⟨765, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨767, by decide +kernel⟩, ⟨734, by decide +kernel⟩),
  (⟨768, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨768, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨770, by decide +kernel⟩, ⟨994, by decide +kernel⟩),
  (⟨771, by decide +kernel⟩, ⟨774, by decide +kernel⟩),
  (⟨771, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨771, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨771, by decide +kernel⟩, ⟨1788, by decide +kernel⟩),
  (⟨771, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨771, by decide +kernel⟩, ⟨1795, by decide +kernel⟩),
  (⟨771, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨771, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨772, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨773, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨776, by decide +kernel⟩, ⟨980, by decide +kernel⟩),
  (⟨782, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨782, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨783, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨783, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨784, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨784, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨786, by decide +kernel⟩, ⟨760, by decide +kernel⟩),
  (⟨786, by decide +kernel⟩, ⟨982, by decide +kernel⟩),
  (⟨787, by decide +kernel⟩, ⟨963, by decide +kernel⟩),
  (⟨787, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨788, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨788, by decide +kernel⟩, ⟨1475, by decide +kernel⟩),
  (⟨788, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨789, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨790, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨791, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨794, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨794, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨794, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨794, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨794, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨794, by decide +kernel⟩, ⟨1065, by decide +kernel⟩),
  (⟨794, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨794, by decide +kernel⟩, ⟨1534, by decide +kernel⟩),
  (⟨794, by decide +kernel⟩, ⟨1615, by decide +kernel⟩),
  (⟨794, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨794, by decide +kernel⟩, ⟨1710, by decide +kernel⟩),
  (⟨794, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨794, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨796, by decide +kernel⟩, ⟨797, by decide +kernel⟩),
  (⟨796, by decide +kernel⟩, ⟨799, by decide +kernel⟩),
  (⟨796, by decide +kernel⟩, ⟨800, by decide +kernel⟩),
  (⟨796, by decide +kernel⟩, ⟨801, by decide +kernel⟩),
  (⟨796, by decide +kernel⟩, ⟨802, by decide +kernel⟩)
]
def edgeBlock25 : List (Fin 1864 × Fin 1864) := [
  (⟨797, by decide +kernel⟩, ⟨802, by decide +kernel⟩),
  (⟨798, by decide +kernel⟩, ⟨802, by decide +kernel⟩),
  (⟨803, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨804, by decide +kernel⟩, ⟨806, by decide +kernel⟩),
  (⟨804, by decide +kernel⟩, ⟨807, by decide +kernel⟩),
  (⟨804, by decide +kernel⟩, ⟨809, by decide +kernel⟩),
  (⟨804, by decide +kernel⟩, ⟨849, by decide +kernel⟩),
  (⟨804, by decide +kernel⟩, ⟨856, by decide +kernel⟩),
  (⟨804, by decide +kernel⟩, ⟨864, by decide +kernel⟩),
  (⟨804, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨804, by decide +kernel⟩, ⟨1169, by decide +kernel⟩),
  (⟨804, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨804, by decide +kernel⟩, ⟨1342, by decide +kernel⟩),
  (⟨804, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨804, by decide +kernel⟩, ⟨1798, by decide +kernel⟩),
  (⟨806, by decide +kernel⟩, ⟨803, by decide +kernel⟩),
  (⟨806, by decide +kernel⟩, ⟨808, by decide +kernel⟩),
  (⟨806, by decide +kernel⟩, ⟨809, by decide +kernel⟩),
  (⟨806, by decide +kernel⟩, ⟨849, by decide +kernel⟩),
  (⟨806, by decide +kernel⟩, ⟨860, by decide +kernel⟩),
  (⟨806, by decide +kernel⟩, ⟨864, by decide +kernel⟩),
  (⟨806, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨806, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨806, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨806, by decide +kernel⟩, ⟨1772, by decide +kernel⟩),
  (⟨806, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨806, by decide +kernel⟩, ⟨1810, by decide +kernel⟩),
  (⟨806, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨807, by decide +kernel⟩, ⟨809, by decide +kernel⟩),
  (⟨808, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨809, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨809, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨809, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨814, by decide +kernel⟩, ⟨1027, by decide +kernel⟩),
  (⟨816, by decide +kernel⟩, ⟨818, by decide +kernel⟩),
  (⟨816, by decide +kernel⟩, ⟨821, by decide +kernel⟩),
  (⟨816, by decide +kernel⟩, ⟨1638, by decide +kernel⟩),
  (⟨816, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨819, by decide +kernel⟩, ⟨827, by decide +kernel⟩),
  (⟨819, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨819, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨820, by decide +kernel⟩, ⟨822, by decide +kernel⟩),
  (⟨820, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨820, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨823, by decide +kernel⟩, ⟨1401, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨816, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨817, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨822, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨823, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨827, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨828, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨831, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨832, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨836, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨839, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨841, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨998, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨1438, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨825, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨826, by decide +kernel⟩, ⟨810, by decide +kernel⟩),
  (⟨826, by decide +kernel⟩, ⟨1554, by decide +kernel⟩)
]
def edgeBlock26 : List (Fin 1864 × Fin 1864) := [
  (⟨826, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨832, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨832, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨832, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨832, by decide +kernel⟩, ⟨1574, by decide +kernel⟩),
  (⟨832, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨832, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨833, by decide +kernel⟩, ⟨812, by decide +kernel⟩),
  (⟨833, by decide +kernel⟩, ⟨840, by decide +kernel⟩),
  (⟨833, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨834, by decide +kernel⟩, ⟨812, by decide +kernel⟩),
  (⟨834, by decide +kernel⟩, ⟨815, by decide +kernel⟩),
  (⟨834, by decide +kernel⟩, ⟨822, by decide +kernel⟩),
  (⟨834, by decide +kernel⟩, ⟨824, by decide +kernel⟩),
  (⟨834, by decide +kernel⟩, ⟨827, by decide +kernel⟩),
  (⟨834, by decide +kernel⟩, ⟨830, by decide +kernel⟩),
  (⟨834, by decide +kernel⟩, ⟨833, by decide +kernel⟩),
  (⟨834, by decide +kernel⟩, ⟨840, by decide +kernel⟩),
  (⟨834, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨834, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨834, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨834, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨835, by decide +kernel⟩, ⟨822, by decide +kernel⟩),
  (⟨835, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨835, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨835, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨837, by decide +kernel⟩, ⟨832, by decide +kernel⟩),
  (⟨837, by decide +kernel⟩, ⟨833, by decide +kernel⟩),
  (⟨838, by decide +kernel⟩, ⟨819, by decide +kernel⟩),
  (⟨838, by decide +kernel⟩, ⟨822, by decide +kernel⟩),
  (⟨838, by decide +kernel⟩, ⟨823, by decide +kernel⟩),
  (⟨838, by decide +kernel⟩, ⟨825, by decide +kernel⟩),
  (⟨838, by decide +kernel⟩, ⟨832, by decide +kernel⟩),
  (⟨838, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨838, by decide +kernel⟩, ⟨998, by decide +kernel⟩),
  (⟨838, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨838, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨838, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨839, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨842, by decide +kernel⟩, ⟨822, by decide +kernel⟩),
  (⟨844, by decide +kernel⟩, ⟨1326, by decide +kernel⟩),
  (⟨849, by decide +kernel⟩, ⟨857, by decide +kernel⟩),
  (⟨849, by decide +kernel⟩, ⟨860, by decide +kernel⟩),
  (⟨849, by decide +kernel⟩, ⟨864, by decide +kernel⟩),
  (⟨849, by decide +kernel⟩, ⟨1798, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨844, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨845, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨846, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨847, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨852, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨853, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨857, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨859, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨860, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨861, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨862, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨863, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨864, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨867, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨1326, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨1365, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨1371, by decide +kernel⟩)
]
def edgeBlock27 : List (Fin 1864 × Fin 1864) := [
  (⟨850, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨1798, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨1801, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨1810, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨1815, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨1819, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨1829, by decide +kernel⟩),
  (⟨850, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨853, by decide +kernel⟩, ⟨856, by decide +kernel⟩),
  (⟨853, by decide +kernel⟩, ⟨865, by decide +kernel⟩),
  (⟨853, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨853, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨853, by decide +kernel⟩, ⟨1828, by decide +kernel⟩),
  (⟨853, by decide +kernel⟩, ⟨1829, by decide +kernel⟩),
  (⟨855, by decide +kernel⟩, ⟨984, by decide +kernel⟩),
  (⟨855, by decide +kernel⟩, ⟨1798, by decide +kernel⟩),
  (⟨859, by decide +kernel⟩, ⟨1326, by decide +kernel⟩),
  (⟨860, by decide +kernel⟩, ⟨1326, by decide +kernel⟩),
  (⟨860, by decide +kernel⟩, ⟨1365, by decide +kernel⟩),
  (⟨860, by decide +kernel⟩, ⟨1371, by decide +kernel⟩),
  (⟨860, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨860, by decide +kernel⟩, ⟨1801, by decide +kernel⟩),
  (⟨862, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨864, by decide +kernel⟩, ⟨845, by decide +kernel⟩),
  (⟨865, by decide +kernel⟩, ⟨866, by decide +kernel⟩),
  (⟨868, by decide +kernel⟩, ⟨987, by decide +kernel⟩),
  (⟨869, by decide +kernel⟩, ⟨987, by decide +kernel⟩),
  (⟨870, by decide +kernel⟩, ⟨987, by decide +kernel⟩),
  (⟨871, by decide +kernel⟩, ⟨987, by decide +kernel⟩),
  (⟨872, by decide +kernel⟩, ⟨987, by decide +kernel⟩),
  (⟨876, by decide +kernel⟩, ⟨959, by decide +kernel⟩),
  (⟨876, by decide +kernel⟩, ⟨975, by decide +kernel⟩),
  (⟨878, by decide +kernel⟩, ⟨879, by decide +kernel⟩),
  (⟨878, by decide +kernel⟩, ⟨880, by decide +kernel⟩),
  (⟨878, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨878, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨879, by decide +kernel⟩, ⟨849, by decide +kernel⟩),
  (⟨879, by decide +kernel⟩, ⟨864, by decide +kernel⟩),
  (⟨879, by decide +kernel⟩, ⟨880, by decide +kernel⟩),
  (⟨879, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨879, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨879, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨879, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨879, by decide +kernel⟩, ⟨1798, by decide +kernel⟩),
  (⟨879, by decide +kernel⟩, ⟨1801, by decide +kernel⟩),
  (⟨880, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨881, by decide +kernel⟩, ⟨884, by decide +kernel⟩),
  (⟨881, by decide +kernel⟩, ⟨885, by decide +kernel⟩),
  (⟨882, by decide +kernel⟩, ⟨877, by decide +kernel⟩),
  (⟨882, by decide +kernel⟩, ⟨883, by decide +kernel⟩),
  (⟨882, by decide +kernel⟩, ⟨885, by decide +kernel⟩),
  (⟨882, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨882, by decide +kernel⟩, ⟨1826, by decide +kernel⟩),
  (⟨883, by decide +kernel⟩, ⟨881, by decide +kernel⟩),
  (⟨883, by decide +kernel⟩, ⟨885, by decide +kernel⟩),
  (⟨885, by decide +kernel⟩, ⟨886, by decide +kernel⟩),
  (⟨887, by decide +kernel⟩, ⟨883, by decide +kernel⟩),
  (⟨888, by decide +kernel⟩, ⟨571, by decide +kernel⟩),
  (⟨888, by decide +kernel⟩, ⟨572, by decide +kernel⟩),
  (⟨888, by decide +kernel⟩, ⟨883, by decide +kernel⟩),
  (⟨888, by decide +kernel⟩, ⟨887, by decide +kernel⟩),
  (⟨888, by decide +kernel⟩, ⟨890, by decide +kernel⟩),
  (⟨888, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨889, by decide +kernel⟩, ⟨991, by decide +kernel⟩)
]
def edgeBlock28 : List (Fin 1864 × Fin 1864) := [
  (⟨889, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨890, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨891, by decide +kernel⟩, ⟨571, by decide +kernel⟩),
  (⟨891, by decide +kernel⟩, ⟨572, by decide +kernel⟩),
  (⟨892, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨894, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨895, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨895, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨895, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨897, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨898, by decide +kernel⟩, ⟨926, by decide +kernel⟩),
  (⟨898, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨898, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨899, by decide +kernel⟩, ⟨903, by decide +kernel⟩),
  (⟨899, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨899, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨900, by decide +kernel⟩, ⟨903, by decide +kernel⟩),
  (⟨900, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨901, by decide +kernel⟩, ⟨903, by decide +kernel⟩),
  (⟨902, by decide +kernel⟩, ⟨897, by decide +kernel⟩),
  (⟨902, by decide +kernel⟩, ⟨903, by decide +kernel⟩),
  (⟨902, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨903, by decide +kernel⟩, ⟨912, by decide +kernel⟩),
  (⟨903, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨905, by decide +kernel⟩, ⟨897, by decide +kernel⟩),
  (⟨905, by decide +kernel⟩, ⟨900, by decide +kernel⟩),
  (⟨905, by decide +kernel⟩, ⟨901, by decide +kernel⟩),
  (⟨905, by decide +kernel⟩, ⟨902, by decide +kernel⟩),
  (⟨905, by decide +kernel⟩, ⟨903, by decide +kernel⟩),
  (⟨905, by decide +kernel⟩, ⟨904, by decide +kernel⟩),
  (⟨905, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨905, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨906, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨906, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨908, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨908, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨909, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨909, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨909, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨910, by decide +kernel⟩, ⟨913, by decide +kernel⟩),
  (⟨910, by decide +kernel⟩, ⟨919, by decide +kernel⟩),
  (⟨910, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨910, by decide +kernel⟩, ⟨1021, by decide +kernel⟩),
  (⟨910, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨910, by decide +kernel⟩, ⟨1246, by decide +kernel⟩),
  (⟨913, by decide +kernel⟩, ⟨915, by decide +kernel⟩),
  (⟨913, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨913, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨914, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨915, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨916, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨917, by decide +kernel⟩, ⟨906, by decide +kernel⟩),
  (⟨919, by decide +kernel⟩, ⟨911, by decide +kernel⟩),
  (⟨919, by decide +kernel⟩, ⟨914, by decide +kernel⟩),
  (⟨919, by decide +kernel⟩, ⟨934, by decide +kernel⟩),
  (⟨919, by decide +kernel⟩, ⟨976, by decide +kernel⟩),
  (⟨919, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨919, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨920, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨920, by decide +kernel⟩, ⟨951, by decide +kernel⟩),
  (⟨921, by decide +kernel⟩, ⟨898, by decide +kernel⟩),
  (⟨921, by decide +kernel⟩, ⟨899, by decide +kernel⟩),
  (⟨921, by decide +kernel⟩, ⟨913, by decide +kernel⟩),
  (⟨921, by decide +kernel⟩, ⟨915, by decide +kernel⟩)
]
def edgeBlock29 : List (Fin 1864 × Fin 1864) := [
  (⟨921, by decide +kernel⟩, ⟨926, by decide +kernel⟩),
  (⟨921, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨921, by decide +kernel⟩, ⟨937, by decide +kernel⟩),
  (⟨921, by decide +kernel⟩, ⟨938, by decide +kernel⟩),
  (⟨921, by decide +kernel⟩, ⟨951, by decide +kernel⟩),
  (⟨921, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨921, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨922, by decide +kernel⟩, ⟨913, by decide +kernel⟩),
  (⟨922, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨922, by decide +kernel⟩, ⟨1000, by decide +kernel⟩),
  (⟨923, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨925, by decide +kernel⟩, ⟨853, by decide +kernel⟩),
  (⟨925, by decide +kernel⟩, ⟨919, by decide +kernel⟩),
  (⟨925, by decide +kernel⟩, ⟨921, by decide +kernel⟩),
  (⟨925, by decide +kernel⟩, ⟨922, by decide +kernel⟩),
  (⟨925, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨925, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨925, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨926, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨927, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨927, by decide +kernel⟩, ⟨933, by decide +kernel⟩),
  (⟨927, by decide +kernel⟩, ⟨950, by decide +kernel⟩),
  (⟨927, by decide +kernel⟩, ⟨956, by decide +kernel⟩),
  (⟨927, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨928, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨928, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨928, by decide +kernel⟩, ⟨1084, by decide +kernel⟩),
  (⟨928, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨929, by decide +kernel⟩, ⟨919, by decide +kernel⟩),
  (⟨929, by decide +kernel⟩, ⟨921, by decide +kernel⟩),
  (⟨929, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨849, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨857, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨864, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨867, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨896, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨912, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨918, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨1798, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨1801, by decide +kernel⟩),
  (⟨930, by decide +kernel⟩, ⟨1811, by decide +kernel⟩),
  (⟨931, by decide +kernel⟩, ⟨1000, by decide +kernel⟩),
  (⟨931, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨933, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨933, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨934, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨935, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨935, by decide +kernel⟩, ⟨936, by decide +kernel⟩),
  (⟨935, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨937, by decide +kernel⟩, ⟨916, by decide +kernel⟩),
  (⟨937, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨937, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨937, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨937, by decide +kernel⟩, ⟨1196, by decide +kernel⟩),
  (⟨937, by decide +kernel⟩, ⟨1205, by decide +kernel⟩),
  (⟨937, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨937, by decide +kernel⟩, ⟨1860, by decide +kernel⟩)
]
def edgeBlock30 : List (Fin 1864 × Fin 1864) := [
  (⟨937, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨938, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨938, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨938, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨938, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨938, by decide +kernel⟩, ⟨1798, by decide +kernel⟩),
  (⟨939, by decide +kernel⟩, ⟨896, by decide +kernel⟩),
  (⟨939, by decide +kernel⟩, ⟨940, by decide +kernel⟩),
  (⟨939, by decide +kernel⟩, ⟨944, by decide +kernel⟩),
  (⟨939, by decide +kernel⟩, ⟨947, by decide +kernel⟩),
  (⟨939, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨939, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨939, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨940, by decide +kernel⟩, ⟨896, by decide +kernel⟩),
  (⟨941, by decide +kernel⟩, ⟨942, by decide +kernel⟩),
  (⟨943, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨945, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨945, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨946, by decide +kernel⟩, ⟨896, by decide +kernel⟩),
  (⟨946, by decide +kernel⟩, ⟨903, by decide +kernel⟩),
  (⟨946, by decide +kernel⟩, ⟨905, by decide +kernel⟩),
  (⟨946, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨946, by decide +kernel⟩, ⟨939, by decide +kernel⟩),
  (⟨946, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨946, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨946, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨947, by decide +kernel⟩, ⟨940, by decide +kernel⟩),
  (⟨947, by decide +kernel⟩, ⟨941, by decide +kernel⟩),
  (⟨947, by decide +kernel⟩, ⟨943, by decide +kernel⟩),
  (⟨947, by decide +kernel⟩, ⟨944, by decide +kernel⟩),
  (⟨947, by decide +kernel⟩, ⟨945, by decide +kernel⟩),
  (⟨949, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨950, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨951, by decide +kernel⟩, ⟨849, by decide +kernel⟩),
  (⟨951, by decide +kernel⟩, ⟨864, by decide +kernel⟩),
  (⟨951, by decide +kernel⟩, ⟨908, by decide +kernel⟩),
  (⟨951, by decide +kernel⟩, ⟨926, by decide +kernel⟩),
  (⟨951, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨951, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨951, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨951, by decide +kernel⟩, ⟨1801, by decide +kernel⟩),
  (⟨952, by decide +kernel⟩, ⟨852, by decide +kernel⟩),
  (⟨952, by decide +kernel⟩, ⟨921, by decide +kernel⟩),
  (⟨952, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨952, by decide +kernel⟩, ⟨1342, by decide +kernel⟩),
  (⟨953, by decide +kernel⟩, ⟨926, by decide +kernel⟩),
  (⟨953, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨953, by decide +kernel⟩, ⟨954, by decide +kernel⟩),
  (⟨953, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨953, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨953, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨953, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨953, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨953, by decide +kernel⟩, ⟨1801, by decide +kernel⟩),
  (⟨954, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨954, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨955, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨955, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨956, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨956, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨956, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨957, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨965, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨966, by decide +kernel⟩, ⟨976, by decide +kernel⟩)
]
def edgeBlock31 : List (Fin 1864 × Fin 1864) := [
  (⟨973, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨987, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨989, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨990, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨992, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1004, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1004, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1004, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1004, by decide +kernel⟩, ⟨1180, by decide +kernel⟩),
  (⟨1004, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1004, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1005, by decide +kernel⟩, ⟨1006, by decide +kernel⟩),
  (⟨1005, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1007, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1007, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1007, by decide +kernel⟩, ⟨1006, by decide +kernel⟩),
  (⟨1007, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1008, by decide +kernel⟩, ⟨1018, by decide +kernel⟩),
  (⟨1009, by decide +kernel⟩, ⟨1010, by decide +kernel⟩),
  (⟨1009, by decide +kernel⟩, ⟨1015, by decide +kernel⟩),
  (⟨1009, by decide +kernel⟩, ⟨1017, by decide +kernel⟩),
  (⟨1009, by decide +kernel⟩, ⟨1019, by decide +kernel⟩),
  (⟨1010, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1010, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1011, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨1011, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1011, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1011, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1011, by decide +kernel⟩, ⟨1009, by decide +kernel⟩),
  (⟨1011, by decide +kernel⟩, ⟨1010, by decide +kernel⟩),
  (⟨1011, by decide +kernel⟩, ⟨1012, by decide +kernel⟩),
  (⟨1011, by decide +kernel⟩, ⟨1015, by decide +kernel⟩),
  (⟨1011, by decide +kernel⟩, ⟨1018, by decide +kernel⟩),
  (⟨1011, by decide +kernel⟩, ⟨1020, by decide +kernel⟩),
  (⟨1011, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1014, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1014, by decide +kernel⟩, ⟨1009, by decide +kernel⟩),
  (⟨1014, by decide +kernel⟩, ⟨1010, by decide +kernel⟩),
  (⟨1014, by decide +kernel⟩, ⟨1011, by decide +kernel⟩),
  (⟨1014, by decide +kernel⟩, ⟨1020, by decide +kernel⟩),
  (⟨1015, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨1016, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1017, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1018, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1018, by decide +kernel⟩, ⟨1009, by decide +kernel⟩),
  (⟨1018, by decide +kernel⟩, ⟨1010, by decide +kernel⟩),
  (⟨1018, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1018, by decide +kernel⟩, ⟨1221, by decide +kernel⟩),
  (⟨1018, by decide +kernel⟩, ⟨1229, by decide +kernel⟩),
  (⟨1022, by decide +kernel⟩, ⟨1021, by decide +kernel⟩),
  (⟨1027, by decide +kernel⟩, ⟨1740, by decide +kernel⟩),
  (⟨1027, by decide +kernel⟩, ⟨1742, by decide +kernel⟩),
  (⟨1027, by decide +kernel⟩, ⟨1747, by decide +kernel⟩),
  (⟨1027, by decide +kernel⟩, ⟨1750, by decide +kernel⟩),
  (⟨1027, by decide +kernel⟩, ⟨1751, by decide +kernel⟩),
  (⟨1027, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1029, by decide +kernel⟩, ⟨905, by decide +kernel⟩),
  (⟨1029, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨1029, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨1029, by decide +kernel⟩, ⟨1030, by decide +kernel⟩),
  (⟨1029, by decide +kernel⟩, ⟨1031, by decide +kernel⟩),
  (⟨1029, by decide +kernel⟩, ⟨1032, by decide +kernel⟩),
  (⟨1029, by decide +kernel⟩, ⟨1033, by decide +kernel⟩),
  (⟨1029, by decide +kernel⟩, ⟨1034, by decide +kernel⟩)
]
def edgeBlock32 : List (Fin 1864 × Fin 1864) := [
  (⟨1029, by decide +kernel⟩, ⟨1035, by decide +kernel⟩),
  (⟨1030, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1030, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨1032, by decide +kernel⟩, ⟨901, by decide +kernel⟩),
  (⟨1032, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨1033, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1033, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨1034, by decide +kernel⟩, ⟨903, by decide +kernel⟩),
  (⟨1034, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨1034, by decide +kernel⟩, ⟨1028, by decide +kernel⟩),
  (⟨1036, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1036, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1036, by decide +kernel⟩, ⟨987, by decide +kernel⟩),
  (⟨1036, by decide +kernel⟩, ⟨988, by decide +kernel⟩),
  (⟨1036, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1036, by decide +kernel⟩, ⟨1096, by decide +kernel⟩),
  (⟨1036, by decide +kernel⟩, ⟨1097, by decide +kernel⟩),
  (⟨1036, by decide +kernel⟩, ⟨1115, by decide +kernel⟩),
  (⟨1036, by decide +kernel⟩, ⟨1116, by decide +kernel⟩),
  (⟨1036, by decide +kernel⟩, ⟨1143, by decide +kernel⟩),
  (⟨1036, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1037, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨1037, by decide +kernel⟩, ⟨1038, by decide +kernel⟩),
  (⟨1037, by decide +kernel⟩, ⟨1039, by decide +kernel⟩),
  (⟨1037, by decide +kernel⟩, ⟨1040, by decide +kernel⟩),
  (⟨1037, by decide +kernel⟩, ⟨1041, by decide +kernel⟩),
  (⟨1038, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1039, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1039, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1039, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1039, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1040, by decide +kernel⟩, ⟨1206, by decide +kernel⟩),
  (⟨1041, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1042, by decide +kernel⟩, ⟨1043, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1042, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1045, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1048, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1049, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1050, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1052, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1053, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1054, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1056, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1059, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1060, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1061, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1063, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1064, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1067, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1068, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1070, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1073, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1075, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1076, by decide +kernel⟩),
  (⟨1044, by decide +kernel⟩, ⟨1079, by decide +kernel⟩),
  (⟨1046, by decide +kernel⟩, ⟨1051, by decide +kernel⟩),
  (⟨1048, by decide +kernel⟩, ⟨1046, by decide +kernel⟩),
  (⟨1048, by decide +kernel⟩, ⟨1047, by decide +kernel⟩),
  (⟨1048, by decide +kernel⟩, ⟨1051, by decide +kernel⟩),
  (⟨1048, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1048, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1050, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1050, by decide +kernel⟩, ⟨1051, by decide +kernel⟩),
  (⟨1051, by decide +kernel⟩, ⟨995, by decide +kernel⟩)
]
def edgeBlock33 : List (Fin 1864 × Fin 1864) := [
  (⟨1056, by decide +kernel⟩, ⟨1055, by decide +kernel⟩),
  (⟨1056, by decide +kernel⟩, ⟨1057, by decide +kernel⟩),
  (⟨1059, by decide +kernel⟩, ⟨1058, by decide +kernel⟩),
  (⟨1060, by decide +kernel⟩, ⟨963, by decide +kernel⟩),
  (⟨1061, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1061, by decide +kernel⟩, ⟨1062, by decide +kernel⟩),
  (⟨1062, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1063, by decide +kernel⟩, ⟨1046, by decide +kernel⟩),
  (⟨1063, by decide +kernel⟩, ⟨1047, by decide +kernel⟩),
  (⟨1063, by decide +kernel⟩, ⟨1149, by decide +kernel⟩),
  (⟨1064, by decide +kernel⟩, ⟨1065, by decide +kernel⟩),
  (⟨1067, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1067, by decide +kernel⟩, ⟨1066, by decide +kernel⟩),
  (⟨1068, by decide +kernel⟩, ⟨802, by decide +kernel⟩),
  (⟨1068, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1068, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1069, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1071, by decide +kernel⟩, ⟨988, by decide +kernel⟩),
  (⟨1071, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1071, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1072, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1073, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1073, by decide +kernel⟩, ⟨1071, by decide +kernel⟩),
  (⟨1073, by decide +kernel⟩, ⟨1072, by decide +kernel⟩),
  (⟨1073, by decide +kernel⟩, ⟨1074, by decide +kernel⟩),
  (⟨1074, by decide +kernel⟩, ⟨1071, by decide +kernel⟩),
  (⟨1075, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1078, by decide +kernel⟩, ⟨1077, by decide +kernel⟩),
  (⟨1079, by decide +kernel⟩, ⟨1077, by decide +kernel⟩),
  (⟨1079, by decide +kernel⟩, ⟨1078, by decide +kernel⟩),
  (⟨1081, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1081, by decide +kernel⟩, ⟨1084, by decide +kernel⟩),
  (⟨1083, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1083, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1083, by decide +kernel⟩, ⟨1084, by decide +kernel⟩),
  (⟨1084, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1084, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1084, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1084, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1085, by decide +kernel⟩, ⟨1081, by decide +kernel⟩),
  (⟨1085, by decide +kernel⟩, ⟨1083, by decide +kernel⟩),
  (⟨1087, by decide +kernel⟩, ⟨1134, by decide +kernel⟩),
  (⟨1088, by decide +kernel⟩, ⟨1134, by decide +kernel⟩),
  (⟨1088, by decide +kernel⟩, ⟨1225, by decide +kernel⟩),
  (⟨1088, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1090, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1092, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1092, by decide +kernel⟩, ⟨1861, by decide +kernel⟩),
  (⟨1094, by decide +kernel⟩, ⟨658, by decide +kernel⟩),
  (⟨1095, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1096, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨1096, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1096, by decide +kernel⟩, ⟨1098, by decide +kernel⟩),
  (⟨1096, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1096, by decide +kernel⟩, ⟨1220, by decide +kernel⟩),
  (⟨1096, by decide +kernel⟩, ⟨1229, by decide +kernel⟩),
  (⟨1097, by decide +kernel⟩, ⟨1116, by decide +kernel⟩),
  (⟨1097, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨1098, by decide +kernel⟩, ⟨1117, by decide +kernel⟩),
  (⟨1098, by decide +kernel⟩, ⟨1129, by decide +kernel⟩),
  (⟨1098, by decide +kernel⟩, ⟨1167, by decide +kernel⟩),
  (⟨1098, by decide +kernel⟩, ⟨1195, by decide +kernel⟩),
  (⟨1098, by decide +kernel⟩, ⟨1229, by decide +kernel⟩),
  (⟨1100, by decide +kernel⟩, ⟨1860, by decide +kernel⟩)
]
def edgeBlock34 : List (Fin 1864 × Fin 1864) := [
  (⟨1101, by decide +kernel⟩, ⟨1113, by decide +kernel⟩),
  (⟨1101, by decide +kernel⟩, ⟨1124, by decide +kernel⟩),
  (⟨1101, by decide +kernel⟩, ⟨1140, by decide +kernel⟩),
  (⟨1102, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1102, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1103, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1103, by decide +kernel⟩, ⟨1146, by decide +kernel⟩),
  (⟨1103, by decide +kernel⟩, ⟨1164, by decide +kernel⟩),
  (⟨1105, by decide +kernel⟩, ⟨1136, by decide +kernel⟩),
  (⟨1105, by decide +kernel⟩, ⟨1137, by decide +kernel⟩),
  (⟨1105, by decide +kernel⟩, ⟨1200, by decide +kernel⟩),
  (⟨1105, by decide +kernel⟩, ⟨1226, by decide +kernel⟩),
  (⟨1105, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1105, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1106, by decide +kernel⟩, ⟨1108, by decide +kernel⟩),
  (⟨1106, by decide +kernel⟩, ⟨1110, by decide +kernel⟩),
  (⟨1106, by decide +kernel⟩, ⟨1196, by decide +kernel⟩),
  (⟨1106, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1106, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1107, by decide +kernel⟩, ⟨658, by decide +kernel⟩),
  (⟨1108, by decide +kernel⟩, ⟨584, by decide +kernel⟩),
  (⟨1108, by decide +kernel⟩, ⟨586, by decide +kernel⟩),
  (⟨1108, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1108, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨1108, by decide +kernel⟩, ⟨1109, by decide +kernel⟩),
  (⟨1108, by decide +kernel⟩, ⟨1186, by decide +kernel⟩),
  (⟨1108, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1108, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1109, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1109, by decide +kernel⟩, ⟨1186, by decide +kernel⟩),
  (⟨1111, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1111, by decide +kernel⟩, ⟨1140, by decide +kernel⟩),
  (⟨1112, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1113, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1113, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1114, by decide +kernel⟩, ⟨1200, by decide +kernel⟩),
  (⟨1115, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨1115, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1118, by decide +kernel⟩, ⟨967, by decide +kernel⟩),
  (⟨1121, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1121, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1121, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨1121, by decide +kernel⟩, ⟨1100, by decide +kernel⟩),
  (⟨1121, by decide +kernel⟩, ⟨1108, by decide +kernel⟩),
  (⟨1121, by decide +kernel⟩, ⟨1186, by decide +kernel⟩),
  (⟨1121, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1091, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1101, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1102, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1108, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1109, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1111, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1121, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1133, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1134, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1135, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1140, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1145, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1180, by decide +kernel⟩)
]
def edgeBlock35 : List (Fin 1864 × Fin 1864) := [
  (⟨1122, by decide +kernel⟩, ⟨1182, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1188, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1190, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1202, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1204, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1215, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1217, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1219, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1122, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1123, by decide +kernel⟩, ⟨965, by decide +kernel⟩),
  (⟨1124, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1124, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1125, by decide +kernel⟩, ⟨1140, by decide +kernel⟩),
  (⟨1125, by decide +kernel⟩, ⟨1172, by decide +kernel⟩),
  (⟨1125, by decide +kernel⟩, ⟨1180, by decide +kernel⟩),
  (⟨1128, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1130, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1130, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1130, by decide +kernel⟩, ⟨1090, by decide +kernel⟩),
  (⟨1130, by decide +kernel⟩, ⟨1131, by decide +kernel⟩),
  (⟨1130, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨1130, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1130, by decide +kernel⟩, ⟨1152, by decide +kernel⟩),
  (⟨1130, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1130, by decide +kernel⟩, ⟨1182, by decide +kernel⟩),
  (⟨1130, by decide +kernel⟩, ⟨1861, by decide +kernel⟩),
  (⟨1131, by decide +kernel⟩, ⟨1104, by decide +kernel⟩),
  (⟨1131, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1132, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1132, by decide +kernel⟩, ⟨972, by decide +kernel⟩),
  (⟨1132, by decide +kernel⟩, ⟨973, by decide +kernel⟩),
  (⟨1132, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1132, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1134, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨1137, by decide +kernel⟩, ⟨1136, by decide +kernel⟩),
  (⟨1141, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨1142, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1142, by decide +kernel⟩, ⟨1159, by decide +kernel⟩),
  (⟨1142, by decide +kernel⟩, ⟨1186, by decide +kernel⟩),
  (⟨1142, by decide +kernel⟩, ⟨1196, by decide +kernel⟩),
  (⟨1142, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1143, by decide +kernel⟩, ⟨1129, by decide +kernel⟩),
  (⟨1144, by decide +kernel⟩, ⟨1182, by decide +kernel⟩),
  (⟨1144, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1145, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1146, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1147, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨1150, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1150, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1150, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1150, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1152, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1152, by decide +kernel⟩, ⟨1159, by decide +kernel⟩),
  (⟨1152, by decide +kernel⟩, ⟨1186, by decide +kernel⟩),
  (⟨1153, by decide +kernel⟩, ⟨1157, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨584, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨730, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨734, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨967, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨997, by decide +kernel⟩)
]
def edgeBlock36 : List (Fin 1864 × Fin 1864) := [
  (⟨1154, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1090, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1092, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1094, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1096, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1098, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1100, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1101, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1102, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1103, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1106, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1107, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1108, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1110, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1112, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1113, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1116, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1120, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1121, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1122, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1123, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1124, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1129, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1130, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1132, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1134, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1135, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1140, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1142, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1147, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1148, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1150, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1152, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1155, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1158, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1166, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1169, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1170, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1171, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1172, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1176, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1177, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1178, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1179, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1181, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1183, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1184, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1185, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1186, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1189, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1191, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1192, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1193, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1196, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1197, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1199, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1203, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1204, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1205, by decide +kernel⟩)
]
def edgeBlock37 : List (Fin 1864 × Fin 1864) := [
  (⟨1154, by decide +kernel⟩, ⟨1209, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1212, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1214, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1215, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1216, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1218, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1220, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1221, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1222, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1223, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1227, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1228, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1229, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1238, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1239, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1861, by decide +kernel⟩),
  (⟨1154, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1155, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1155, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1155, by decide +kernel⟩, ⟨1169, by decide +kernel⟩),
  (⟨1155, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1155, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1156, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨1156, by decide +kernel⟩, ⟨1153, by decide +kernel⟩),
  (⟨1157, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨1158, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1158, by decide +kernel⟩, ⟨1159, by decide +kernel⟩),
  (⟨1158, by decide +kernel⟩, ⟨1186, by decide +kernel⟩),
  (⟨1160, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1160, by decide +kernel⟩, ⟨1229, by decide +kernel⟩),
  (⟨1161, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1161, by decide +kernel⟩, ⟨1164, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨584, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨737, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨962, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨987, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1101, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1115, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1130, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1133, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1135, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1140, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1143, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1148, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1150, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1151, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1153, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1154, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1156, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1157, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1161, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1163, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1169, by decide +kernel⟩)
]
def edgeBlock38 : List (Fin 1864 × Fin 1864) := [
  (⟨1162, by decide +kernel⟩, ⟨1172, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1176, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1186, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1201, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1208, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1215, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1218, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1221, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1222, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1223, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1162, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨983, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨1090, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨1098, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨1130, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨1132, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨1153, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨1157, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨1164, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨1213, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨1229, by decide +kernel⟩),
  (⟨1163, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1166, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨1166, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1166, by decide +kernel⟩, ⟨1135, by decide +kernel⟩),
  (⟨1166, by decide +kernel⟩, ⟨1142, by decide +kernel⟩),
  (⟨1166, by decide +kernel⟩, ⟨1148, by decide +kernel⟩),
  (⟨1166, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1166, by decide +kernel⟩, ⟨1215, by decide +kernel⟩),
  (⟨1166, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1168, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1170, by decide +kernel⟩, ⟨988, by decide +kernel⟩),
  (⟨1170, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1170, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1170, by decide +kernel⟩, ⟨1089, by decide +kernel⟩),
  (⟨1170, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨1170, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1170, by decide +kernel⟩, ⟨1148, by decide +kernel⟩),
  (⟨1170, by decide +kernel⟩, ⟨1156, by decide +kernel⟩),
  (⟨1171, by decide +kernel⟩, ⟨1170, by decide +kernel⟩),
  (⟨1172, by decide +kernel⟩, ⟨1102, by decide +kernel⟩),
  (⟨1172, by decide +kernel⟩, ⟨1105, by decide +kernel⟩),
  (⟨1172, by decide +kernel⟩, ⟨1113, by decide +kernel⟩),
  (⟨1172, by decide +kernel⟩, ⟨1114, by decide +kernel⟩),
  (⟨1172, by decide +kernel⟩, ⟨1119, by decide +kernel⟩),
  (⟨1172, by decide +kernel⟩, ⟨1124, by decide +kernel⟩),
  (⟨1172, by decide +kernel⟩, ⟨1138, by decide +kernel⟩),
  (⟨1172, by decide +kernel⟩, ⟨1144, by decide +kernel⟩),
  (⟨1172, by decide +kernel⟩, ⟨1165, by decide +kernel⟩),
  (⟨1172, by decide +kernel⟩, ⟨1168, by decide +kernel⟩),
  (⟨1172, by decide +kernel⟩, ⟨1207, by decide +kernel⟩),
  (⟨1172, by decide +kernel⟩, ⟨1210, by decide +kernel⟩),
  (⟨1172, by decide +kernel⟩, ⟨1225, by decide +kernel⟩),
  (⟨1172, by decide +kernel⟩, ⟨1230, by decide +kernel⟩),
  (⟨1172, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1174, by decide +kernel⟩, ⟨1175, by decide +kernel⟩),
  (⟨1174, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1176, by decide +kernel⟩, ⟨965, by decide +kernel⟩)
]
def edgeBlock39 : List (Fin 1864 × Fin 1864) := [
  (⟨1176, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1176, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1176, by decide +kernel⟩, ⟨1861, by decide +kernel⟩),
  (⟨1177, by decide +kernel⟩, ⟨1148, by decide +kernel⟩),
  (⟨1177, by decide +kernel⟩, ⟨1176, by decide +kernel⟩),
  (⟨1178, by decide +kernel⟩, ⟨1238, by decide +kernel⟩),
  (⟨1179, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1179, by decide +kernel⟩, ⟨1148, by decide +kernel⟩),
  (⟨1179, by decide +kernel⟩, ⟨1152, by decide +kernel⟩),
  (⟨1179, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1179, by decide +kernel⟩, ⟨1203, by decide +kernel⟩),
  (⟨1179, by decide +kernel⟩, ⟨1209, by decide +kernel⟩),
  (⟨1179, by decide +kernel⟩, ⟨1211, by decide +kernel⟩),
  (⟨1179, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1181, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1181, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1181, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1181, by decide +kernel⟩, ⟨1152, by decide +kernel⟩),
  (⟨1181, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1181, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1183, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1183, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1183, by decide +kernel⟩, ⟨1108, by decide +kernel⟩),
  (⟨1183, by decide +kernel⟩, ⟨1196, by decide +kernel⟩),
  (⟨1183, by decide +kernel⟩, ⟨1205, by decide +kernel⟩),
  (⟨1183, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1183, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1184, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1184, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1185, by decide +kernel⟩, ⟨988, by decide +kernel⟩),
  (⟨1185, by decide +kernel⟩, ⟨1130, by decide +kernel⟩),
  (⟨1185, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨1185, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1185, by decide +kernel⟩, ⟨1198, by decide +kernel⟩),
  (⟨1185, by decide +kernel⟩, ⟨1216, by decide +kernel⟩),
  (⟨1186, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1188, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1189, by decide +kernel⟩, ⟨1191, by decide +kernel⟩),
  (⟨1189, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1189, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1191, by decide +kernel⟩, ⟨1186, by decide +kernel⟩),
  (⟨1191, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1192, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1192, by decide +kernel⟩, ⟨1191, by decide +kernel⟩),
  (⟨1193, by decide +kernel⟩, ⟨722, by decide +kernel⟩),
  (⟨1194, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1195, by decide +kernel⟩, ⟨1187, by decide +kernel⟩),
  (⟨1195, by decide +kernel⟩, ⟨1194, by decide +kernel⟩),
  (⟨1196, by decide +kernel⟩, ⟨1186, by decide +kernel⟩),
  (⟨1197, by decide +kernel⟩, ⟨1089, by decide +kernel⟩),
  (⟨1197, by decide +kernel⟩, ⟨1213, by decide +kernel⟩),
  (⟨1199, by decide +kernel⟩, ⟨1090, by decide +kernel⟩),
  (⟨1199, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1199, by decide +kernel⟩, ⟨1148, by decide +kernel⟩),
  (⟨1199, by decide +kernel⟩, ⟨1209, by decide +kernel⟩),
  (⟨1199, by decide +kernel⟩, ⟨1216, by decide +kernel⟩),
  (⟨1203, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1204, by decide +kernel⟩, ⟨1117, by decide +kernel⟩),
  (⟨1204, by decide +kernel⟩, ⟨1129, by decide +kernel⟩),
  (⟨1204, by decide +kernel⟩, ⟨1195, by decide +kernel⟩),
  (⟨1204, by decide +kernel⟩, ⟨1229, by decide +kernel⟩),
  (⟨1206, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨1208, by decide +kernel⟩, ⟨1089, by decide +kernel⟩),
  (⟨1208, by decide +kernel⟩, ⟨1090, by decide +kernel⟩)
]
def edgeBlock40 : List (Fin 1864 × Fin 1864) := [
  (⟨1209, by decide +kernel⟩, ⟨1090, by decide +kernel⟩),
  (⟨1209, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1209, by decide +kernel⟩, ⟨1148, by decide +kernel⟩),
  (⟨1209, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1209, by decide +kernel⟩, ⟨1198, by decide +kernel⟩),
  (⟨1209, by decide +kernel⟩, ⟨1203, by decide +kernel⟩),
  (⟨1209, by decide +kernel⟩, ⟨1204, by decide +kernel⟩),
  (⟨1209, by decide +kernel⟩, ⟨1211, by decide +kernel⟩),
  (⟨1211, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1211, by decide +kernel⟩, ⟨1203, by decide +kernel⟩),
  (⟨1212, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1214, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1215, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1215, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1216, by decide +kernel⟩, ⟨988, by decide +kernel⟩),
  (⟨1216, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨1216, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1216, by decide +kernel⟩, ⟨1148, by decide +kernel⟩),
  (⟨1217, by decide +kernel⟩, ⟨1137, by decide +kernel⟩),
  (⟨1218, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1218, by decide +kernel⟩, ⟨1125, by decide +kernel⟩),
  (⟨1218, by decide +kernel⟩, ⟨1134, by decide +kernel⟩),
  (⟨1218, by decide +kernel⟩, ⟨1182, by decide +kernel⟩),
  (⟨1218, by decide +kernel⟩, ⟨1219, by decide +kernel⟩),
  (⟨1218, by decide +kernel⟩, ⟨1223, by decide +kernel⟩),
  (⟨1218, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1219, by decide +kernel⟩, ⟨967, by decide +kernel⟩),
  (⟨1219, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1219, by decide +kernel⟩, ⟨1093, by decide +kernel⟩),
  (⟨1219, by decide +kernel⟩, ⟨1111, by decide +kernel⟩),
  (⟨1219, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1219, by decide +kernel⟩, ⟨1204, by decide +kernel⟩),
  (⟨1219, by decide +kernel⟩, ⟨1215, by decide +kernel⟩),
  (⟨1220, by decide +kernel⟩, ⟨1148, by decide +kernel⟩),
  (⟨1220, by decide +kernel⟩, ⟨1218, by decide +kernel⟩),
  (⟨1220, by decide +kernel⟩, ⟨1222, by decide +kernel⟩),
  (⟨1221, by decide +kernel⟩, ⟨967, by decide +kernel⟩),
  (⟨1221, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1221, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1221, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1221, by decide +kernel⟩, ⟨1092, by decide +kernel⟩),
  (⟨1221, by decide +kernel⟩, ⟨1109, by decide +kernel⟩),
  (⟨1221, by decide +kernel⟩, ⟨1135, by decide +kernel⟩),
  (⟨1221, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨1221, by decide +kernel⟩, ⟨1140, by decide +kernel⟩),
  (⟨1221, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1221, by decide +kernel⟩, ⟨1186, by decide +kernel⟩),
  (⟨1221, by decide +kernel⟩, ⟨1204, by decide +kernel⟩),
  (⟨1221, by decide +kernel⟩, ⟨1229, by decide +kernel⟩),
  (⟨1221, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1221, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1088, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1099, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1101, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1106, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1108, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1111, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1118, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1121, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1122, by decide +kernel⟩)
]
def edgeBlock41 : List (Fin 1864 × Fin 1864) := [
  (⟨1222, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1128, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1133, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1134, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1135, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1140, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1142, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1174, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1180, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1182, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1189, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1196, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1201, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1205, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1214, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1215, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1221, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1223, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1224, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1225, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1222, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1091, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1092, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1095, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1111, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1121, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1126, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1134, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1135, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1140, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1145, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1146, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1164, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1172, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1173, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1188, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1201, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1204, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1217, by decide +kernel⟩),
  (⟨1223, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1227, by decide +kernel⟩, ⟨988, by decide +kernel⟩),
  (⟨1227, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1227, by decide +kernel⟩, ⟨1134, by decide +kernel⟩),
  (⟨1227, by decide +kernel⟩, ⟨1135, by decide +kernel⟩),
  (⟨1227, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1227, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1228, by decide +kernel⟩, ⟨1092, by decide +kernel⟩),
  (⟨1228, by decide +kernel⟩, ⟨1135, by decide +kernel⟩),
  (⟨1228, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1228, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1228, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1233, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1233, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1233, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1233, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1233, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1234, by decide +kernel⟩, ⟨971, by decide +kernel⟩)
]
def edgeBlock42 : List (Fin 1864 × Fin 1864) := [
  (⟨1234, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1234, by decide +kernel⟩, ⟨998, by decide +kernel⟩),
  (⟨1234, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨1234, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨1234, by decide +kernel⟩, ⟨1233, by decide +kernel⟩),
  (⟨1235, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1235, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1235, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨1235, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨1236, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1236, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1236, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨1236, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1236, by decide +kernel⟩, ⟨1237, by decide +kernel⟩),
  (⟨1237, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1238, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨1238, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨1238, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1238, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1239, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨1239, by decide +kernel⟩, ⟨1176, by decide +kernel⟩),
  (⟨1239, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1241, by decide +kernel⟩, ⟨985, by decide +kernel⟩),
  (⟨1241, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1242, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1242, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1242, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨1242, by decide +kernel⟩, ⟨1243, by decide +kernel⟩),
  (⟨1242, by decide +kernel⟩, ⟨1739, by decide +kernel⟩),
  (⟨1243, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1243, by decide +kernel⟩, ⟨1739, by decide +kernel⟩),
  (⟨1243, by decide +kernel⟩, ⟨1750, by decide +kernel⟩),
  (⟨1243, by decide +kernel⟩, ⟨1751, by decide +kernel⟩),
  (⟨1243, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1244, by decide +kernel⟩, ⟨985, by decide +kernel⟩),
  (⟨1244, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨1244, by decide +kernel⟩, ⟨1245, by decide +kernel⟩),
  (⟨1244, by decide +kernel⟩, ⟨1246, by decide +kernel⟩),
  (⟨1244, by decide +kernel⟩, ⟨1250, by decide +kernel⟩),
  (⟨1248, by decide +kernel⟩, ⟨1244, by decide +kernel⟩),
  (⟨1248, by decide +kernel⟩, ⟨1246, by decide +kernel⟩),
  (⟨1248, by decide +kernel⟩, ⟨1247, by decide +kernel⟩),
  (⟨1248, by decide +kernel⟩, ⟨1249, by decide +kernel⟩),
  (⟨1250, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨1251, by decide +kernel⟩, ⟨1244, by decide +kernel⟩),
  (⟨1252, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1252, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1253, by decide +kernel⟩, ⟨1252, by decide +kernel⟩),
  (⟨1254, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1254, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1255, by decide +kernel⟩, ⟨1254, by decide +kernel⟩),
  (⟨1256, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨1256, by decide +kernel⟩, ⟨1253, by decide +kernel⟩),
  (⟨1256, by decide +kernel⟩, ⟨1255, by decide +kernel⟩),
  (⟨1256, by decide +kernel⟩, ⟨1257, by decide +kernel⟩),
  (⟨1257, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1257, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1258, by decide +kernel⟩, ⟨658, by decide +kernel⟩),
  (⟨1258, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1258, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1258, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨1261, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨1261, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1261, by decide +kernel⟩, ⟨991, by decide +kernel⟩)
]
def edgeBlock43 : List (Fin 1864 × Fin 1864) := [
  (⟨1261, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨1261, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1262, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1263, by decide +kernel⟩, ⟨1261, by decide +kernel⟩),
  (⟨1264, by decide +kernel⟩, ⟨1023, by decide +kernel⟩),
  (⟨1264, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨1264, by decide +kernel⟩, ⟨1261, by decide +kernel⟩),
  (⟨1264, by decide +kernel⟩, ⟨1263, by decide +kernel⟩),
  (⟨1266, by decide +kernel⟩, ⟨877, by decide +kernel⟩),
  (⟨1266, by decide +kernel⟩, ⟨880, by decide +kernel⟩),
  (⟨1266, by decide +kernel⟩, ⟨1271, by decide +kernel⟩),
  (⟨1268, by decide +kernel⟩, ⟨879, by decide +kernel⟩),
  (⟨1268, by decide +kernel⟩, ⟨880, by decide +kernel⟩),
  (⟨1270, by decide +kernel⟩, ⟨572, by decide +kernel⟩),
  (⟨1270, by decide +kernel⟩, ⟨856, by decide +kernel⟩),
  (⟨1270, by decide +kernel⟩, ⟨882, by decide +kernel⟩),
  (⟨1270, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨1270, by decide +kernel⟩, ⟨1269, by decide +kernel⟩),
  (⟨1270, by decide +kernel⟩, ⟨1273, by decide +kernel⟩),
  (⟨1271, by decide +kernel⟩, ⟨879, by decide +kernel⟩),
  (⟨1271, by decide +kernel⟩, ⟨880, by decide +kernel⟩),
  (⟨1271, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨1272, by decide +kernel⟩, ⟨877, by decide +kernel⟩),
  (⟨1272, by decide +kernel⟩, ⟨880, by decide +kernel⟩),
  (⟨1272, by decide +kernel⟩, ⟨1271, by decide +kernel⟩),
  (⟨1273, by decide +kernel⟩, ⟨880, by decide +kernel⟩),
  (⟨1273, by decide +kernel⟩, ⟨1267, by decide +kernel⟩),
  (⟨1273, by decide +kernel⟩, ⟨1268, by decide +kernel⟩),
  (⟨1273, by decide +kernel⟩, ⟨1272, by decide +kernel⟩),
  (⟨1273, by decide +kernel⟩, ⟨1274, by decide +kernel⟩),
  (⟨1274, by decide +kernel⟩, ⟨879, by decide +kernel⟩),
  (⟨1274, by decide +kernel⟩, ⟨880, by decide +kernel⟩),
  (⟨1274, by decide +kernel⟩, ⟨1268, by decide +kernel⟩),
  (⟨1274, by decide +kernel⟩, ⟨1271, by decide +kernel⟩),
  (⟨1274, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1274, by decide +kernel⟩, ⟨1798, by decide +kernel⟩),
  (⟨1275, by decide +kernel⟩, ⟨1295, by decide +kernel⟩),
  (⟨1276, by decide +kernel⟩, ⟨846, by decide +kernel⟩),
  (⟨1276, by decide +kernel⟩, ⟨863, by decide +kernel⟩),
  (⟨1276, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1276, by decide +kernel⟩, ⟨1275, by decide +kernel⟩),
  (⟨1276, by decide +kernel⟩, ⟨1283, by decide +kernel⟩),
  (⟨1276, by decide +kernel⟩, ⟨1286, by decide +kernel⟩),
  (⟨1276, by decide +kernel⟩, ⟨1775, by decide +kernel⟩),
  (⟨1276, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1276, by decide +kernel⟩, ⟨1799, by decide +kernel⟩),
  (⟨1276, by decide +kernel⟩, ⟨1804, by decide +kernel⟩),
  (⟨1276, by decide +kernel⟩, ⟨1805, by decide +kernel⟩),
  (⟨1276, by decide +kernel⟩, ⟨1817, by decide +kernel⟩),
  (⟨1276, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨1276, by decide +kernel⟩, ⟨1831, by decide +kernel⟩),
  (⟨1277, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1277, by decide +kernel⟩, ⟨1295, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨609, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨863, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1276, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1277, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1278, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1280, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1281, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1282, by decide +kernel⟩)
]
def edgeBlock44 : List (Fin 1864 × Fin 1864) := [
  (⟨1279, by decide +kernel⟩, ⟨1285, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1301, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1305, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1306, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1311, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1312, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1318, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1329, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1330, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1339, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1343, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1718, by decide +kernel⟩),
  (⟨1279, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1280, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨1280, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1281, by decide +kernel⟩, ⟨879, by decide +kernel⟩),
  (⟨1281, by decide +kernel⟩, ⟨880, by decide +kernel⟩),
  (⟨1281, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨1281, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1281, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨1281, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨1281, by decide +kernel⟩, ⟨1328, by decide +kernel⟩),
  (⟨1281, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1281, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1282, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1282, by decide +kernel⟩, ⟨1301, by decide +kernel⟩),
  (⟨1282, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨1283, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1283, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1285, by decide +kernel⟩, ⟨1284, by decide +kernel⟩),
  (⟨1285, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1285, by decide +kernel⟩, ⟨1801, by decide +kernel⟩),
  (⟨1286, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1289, by decide +kernel⟩, ⟨851, by decide +kernel⟩),
  (⟨1289, by decide +kernel⟩, ⟨852, by decide +kernel⟩),
  (⟨1289, by decide +kernel⟩, ⟨853, by decide +kernel⟩),
  (⟨1289, by decide +kernel⟩, ⟨863, by decide +kernel⟩),
  (⟨1289, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨1289, by decide +kernel⟩, ⟨1287, by decide +kernel⟩),
  (⟨1289, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1289, by decide +kernel⟩, ⟨1806, by decide +kernel⟩),
  (⟨1289, by decide +kernel⟩, ⟨1809, by decide +kernel⟩),
  (⟨1289, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨416, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨426, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨427, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨428, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨430, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨571, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨572, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨670, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨737, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨848, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨851, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨852, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨853, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨854, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨858, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨859, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨863, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨864, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨953, by decide +kernel⟩)
]
def edgeBlock45 : List (Fin 1864 × Fin 1864) := [
  (⟨1291, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨985, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨1288, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨1348, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨1354, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨1360, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨1798, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨1806, by decide +kernel⟩),
  (⟨1291, by decide +kernel⟩, ⟨1829, by decide +kernel⟩),
  (⟨1292, by decide +kernel⟩, ⟨848, by decide +kernel⟩),
  (⟨1292, by decide +kernel⟩, ⟨853, by decide +kernel⟩),
  (⟨1293, by decide +kernel⟩, ⟨593, by decide +kernel⟩),
  (⟨1293, by decide +kernel⟩, ⟨736, by decide +kernel⟩),
  (⟨1293, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1293, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1293, by decide +kernel⟩, ⟨1279, by decide +kernel⟩),
  (⟨1293, by decide +kernel⟩, ⟨1285, by decide +kernel⟩),
  (⟨1293, by decide +kernel⟩, ⟨1289, by decide +kernel⟩),
  (⟨1293, by decide +kernel⟩, ⟨1290, by decide +kernel⟩),
  (⟨1293, by decide +kernel⟩, ⟨1291, by decide +kernel⟩),
  (⟨1293, by decide +kernel⟩, ⟨1292, by decide +kernel⟩),
  (⟨1293, by decide +kernel⟩, ⟨1298, by decide +kernel⟩),
  (⟨1293, by decide +kernel⟩, ⟨1807, by decide +kernel⟩),
  (⟨1294, by decide +kernel⟩, ⟨67, by decide +kernel⟩),
  (⟨1294, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1294, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨1294, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1294, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨1295, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1296, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1296, by decide +kernel⟩, ⟨1365, by decide +kernel⟩),
  (⟨1297, by decide +kernel⟩, ⟨849, by decide +kernel⟩),
  (⟨1297, by decide +kernel⟩, ⟨864, by decide +kernel⟩),
  (⟨1297, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1299, by decide +kernel⟩, ⟨1300, by decide +kernel⟩),
  (⟨1299, by decide +kernel⟩, ⟨1303, by decide +kernel⟩),
  (⟨1299, by decide +kernel⟩, ⟨1336, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1295, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1302, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1309, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1310, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1319, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1322, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1325, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1329, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1331, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1335, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1337, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1367, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1802, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1817, by decide +kernel⟩),
  (⟨1300, by decide +kernel⟩, ⟨1831, by decide +kernel⟩),
  (⟨1301, by decide +kernel⟩, ⟨78, by decide +kernel⟩),
  (⟨1301, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1301, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1301, by decide +kernel⟩, ⟨1295, by decide +kernel⟩),
  (⟨1301, by decide +kernel⟩, ⟨1299, by decide +kernel⟩),
  (⟨1301, by decide +kernel⟩, ⟨1314, by decide +kernel⟩),
  (⟨1301, by decide +kernel⟩, ⟨1317, by decide +kernel⟩),
  (⟨1301, by decide +kernel⟩, ⟨1318, by decide +kernel⟩)
]
def edgeBlock46 : List (Fin 1864 × Fin 1864) := [
  (⟨1301, by decide +kernel⟩, ⟨1324, by decide +kernel⟩),
  (⟨1301, by decide +kernel⟩, ⟨1333, by decide +kernel⟩),
  (⟨1301, by decide +kernel⟩, ⟨1344, by decide +kernel⟩),
  (⟨1301, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1302, by decide +kernel⟩, ⟨1304, by decide +kernel⟩),
  (⟨1302, by decide +kernel⟩, ⟨1340, by decide +kernel⟩),
  (⟨1302, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1302, by decide +kernel⟩, ⟨1805, by decide +kernel⟩),
  (⟨1303, by decide +kernel⟩, ⟨1304, by decide +kernel⟩),
  (⟨1303, by decide +kernel⟩, ⟨1305, by decide +kernel⟩),
  (⟨1303, by decide +kernel⟩, ⟨1321, by decide +kernel⟩),
  (⟨1303, by decide +kernel⟩, ⟨1328, by decide +kernel⟩),
  (⟨1303, by decide +kernel⟩, ⟨1340, by decide +kernel⟩),
  (⟨1303, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1303, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨1305, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1305, by decide +kernel⟩, ⟨1297, by decide +kernel⟩),
  (⟨1305, by decide +kernel⟩, ⟨1306, by decide +kernel⟩),
  (⟨1305, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1306, by decide +kernel⟩, ⟨857, by decide +kernel⟩),
  (⟨1306, by decide +kernel⟩, ⟨1296, by decide +kernel⟩),
  (⟨1306, by decide +kernel⟩, ⟨1332, by decide +kernel⟩),
  (⟨1306, by decide +kernel⟩, ⟨1335, by decide +kernel⟩),
  (⟨1306, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1306, by decide +kernel⟩, ⟨1801, by decide +kernel⟩),
  (⟨1307, by decide +kernel⟩, ⟨1320, by decide +kernel⟩),
  (⟨1307, by decide +kernel⟩, ⟨1367, by decide +kernel⟩),
  (⟨1307, by decide +kernel⟩, ⟨1372, by decide +kernel⟩),
  (⟨1307, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1308, by decide +kernel⟩, ⟨1307, by decide +kernel⟩),
  (⟨1309, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1310, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1311, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1311, by decide +kernel⟩, ⟨1295, by decide +kernel⟩),
  (⟨1311, by decide +kernel⟩, ⟨1299, by decide +kernel⟩),
  (⟨1311, by decide +kernel⟩, ⟨1301, by decide +kernel⟩),
  (⟨1311, by decide +kernel⟩, ⟨1314, by decide +kernel⟩),
  (⟨1311, by decide +kernel⟩, ⟨1318, by decide +kernel⟩),
  (⟨1311, by decide +kernel⟩, ⟨1324, by decide +kernel⟩),
  (⟨1311, by decide +kernel⟩, ⟨1333, by decide +kernel⟩),
  (⟨1311, by decide +kernel⟩, ⟨1344, by decide +kernel⟩),
  (⟨1314, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1314, by decide +kernel⟩, ⟨1295, by decide +kernel⟩),
  (⟨1314, by decide +kernel⟩, ⟨1819, by decide +kernel⟩),
  (⟨1314, by decide +kernel⟩, ⟨1823, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨67, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨68, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨71, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨74, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨76, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨79, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨81, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨1305, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨1308, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨1322, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨1323, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨1328, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨1331, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨1336, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨1340, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨1363, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨1367, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨1370, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨1794, by decide +kernel⟩)
]
def edgeBlock47 : List (Fin 1864 × Fin 1864) := [
  (⟨1316, by decide +kernel⟩, ⟨1814, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨1820, by decide +kernel⟩),
  (⟨1316, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨63, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨65, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨69, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨70, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨81, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1294, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1295, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1310, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1316, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1318, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1323, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1331, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1334, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1335, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1336, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1341, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1367, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1802, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1805, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1817, by decide +kernel⟩),
  (⟨1317, by decide +kernel⟩, ⟨1831, by decide +kernel⟩),
  (⟨1318, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1319, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨1319, by decide +kernel⟩, ⟨1331, by decide +kernel⟩),
  (⟨1319, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1321, by decide +kernel⟩, ⟨74, by decide +kernel⟩),
  (⟨1321, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1321, by decide +kernel⟩, ⟨1304, by decide +kernel⟩),
  (⟨1321, by decide +kernel⟩, ⟨1308, by decide +kernel⟩),
  (⟨1321, by decide +kernel⟩, ⟨1323, by decide +kernel⟩),
  (⟨1321, by decide +kernel⟩, ⟨1327, by decide +kernel⟩),
  (⟨1321, by decide +kernel⟩, ⟨1331, by decide +kernel⟩),
  (⟨1321, by decide +kernel⟩, ⟨1340, by decide +kernel⟩),
  (⟨1321, by decide +kernel⟩, ⟨1367, by decide +kernel⟩),
  (⟨1321, by decide +kernel⟩, ⟨1370, by decide +kernel⟩),
  (⟨1321, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1321, by decide +kernel⟩, ⟨1801, by decide +kernel⟩),
  (⟨1321, by decide +kernel⟩, ⟨1811, by decide +kernel⟩),
  (⟨1321, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨1322, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨1322, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1324, by decide +kernel⟩, ⟨849, by decide +kernel⟩),
  (⟨1324, by decide +kernel⟩, ⟨864, by decide +kernel⟩),
  (⟨1324, by decide +kernel⟩, ⟨1323, by decide +kernel⟩),
  (⟨1324, by decide +kernel⟩, ⟨1810, by decide +kernel⟩),
  (⟨1325, by decide +kernel⟩, ⟨1821, by decide +kernel⟩),
  (⟨1326, by decide +kernel⟩, ⟨1315, by decide +kernel⟩),
  (⟨1327, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨1327, by decide +kernel⟩, ⟨1319, by decide +kernel⟩),
  (⟨1327, by decide +kernel⟩, ⟨1363, by decide +kernel⟩),
  (⟨1327, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1327, by decide +kernel⟩, ⟨1814, by decide +kernel⟩),
  (⟨1327, by decide +kernel⟩, ⟨1820, by decide +kernel⟩),
  (⟨1327, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨1328, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨1329, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨1329, by decide +kernel⟩, ⟨1318, by decide +kernel⟩),
  (⟨1330, by decide +kernel⟩, ⟨1329, by decide +kernel⟩)
]
def edgeBlock48 : List (Fin 1864 × Fin 1864) := [
  (⟨1330, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1331, by decide +kernel⟩, ⟨1329, by decide +kernel⟩),
  (⟨1332, by decide +kernel⟩, ⟨849, by decide +kernel⟩),
  (⟨1334, by decide +kernel⟩, ⟨72, by decide +kernel⟩),
  (⟨1334, by decide +kernel⟩, ⟨1336, by decide +kernel⟩),
  (⟨1334, by decide +kernel⟩, ⟨1367, by decide +kernel⟩),
  (⟨1334, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1335, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨1335, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1335, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1336, by decide +kernel⟩, ⟨849, by decide +kernel⟩),
  (⟨1336, by decide +kernel⟩, ⟨864, by decide +kernel⟩),
  (⟨1336, by decide +kernel⟩, ⟨867, by decide +kernel⟩),
  (⟨1336, by decide +kernel⟩, ⟨1323, by decide +kernel⟩),
  (⟨1336, by decide +kernel⟩, ⟨1326, by decide +kernel⟩),
  (⟨1336, by decide +kernel⟩, ⟨1365, by decide +kernel⟩),
  (⟨1336, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1336, by decide +kernel⟩, ⟨1801, by decide +kernel⟩),
  (⟨1336, by decide +kernel⟩, ⟨1811, by decide +kernel⟩),
  (⟨1337, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1340, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1341, by decide +kernel⟩, ⟨1302, by decide +kernel⟩),
  (⟨1341, by decide +kernel⟩, ⟨1340, by decide +kernel⟩),
  (⟨1341, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1342, by decide +kernel⟩, ⟨852, by decide +kernel⟩),
  (⟨1342, by decide +kernel⟩, ⟨853, by decide +kernel⟩),
  (⟨1342, by decide +kernel⟩, ⟨859, by decide +kernel⟩),
  (⟨1342, by decide +kernel⟩, ⟨864, by decide +kernel⟩),
  (⟨1342, by decide +kernel⟩, ⟨953, by decide +kernel⟩),
  (⟨1342, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1342, by decide +kernel⟩, ⟨1288, by decide +kernel⟩),
  (⟨1342, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1342, by decide +kernel⟩, ⟨1798, by decide +kernel⟩),
  (⟨1343, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨1343, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1343, by decide +kernel⟩, ⟨1820, by decide +kernel⟩),
  (⟨1343, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨1344, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨1344, by decide +kernel⟩, ⟨1329, by decide +kernel⟩),
  (⟨1344, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1344, by decide +kernel⟩, ⟨1820, by decide +kernel⟩),
  (⟨1344, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨1345, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨1345, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1346, by decide +kernel⟩, ⟨1355, by decide +kernel⟩),
  (⟨1347, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1347, by decide +kernel⟩, ⟨1002, by decide +kernel⟩),
  (⟨1349, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1349, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1349, by decide +kernel⟩, ⟨1346, by decide +kernel⟩),
  (⟨1349, by decide +kernel⟩, ⟨1347, by decide +kernel⟩),
  (⟨1349, by decide +kernel⟩, ⟨1348, by decide +kernel⟩),
  (⟨1349, by decide +kernel⟩, ⟨1350, by decide +kernel⟩),
  (⟨1349, by decide +kernel⟩, ⟨1353, by decide +kernel⟩),
  (⟨1349, by decide +kernel⟩, ⟨1354, by decide +kernel⟩),
  (⟨1349, by decide +kernel⟩, ⟨1359, by decide +kernel⟩),
  (⟨1350, by decide +kernel⟩, ⟨1358, by decide +kernel⟩),
  (⟨1351, by decide +kernel⟩, ⟨1024, by decide +kernel⟩),
  (⟨1351, by decide +kernel⟩, ⟨1348, by decide +kernel⟩),
  (⟨1351, by decide +kernel⟩, ⟨1350, by decide +kernel⟩),
  (⟨1351, by decide +kernel⟩, ⟨1353, by decide +kernel⟩),
  (⟨1351, by decide +kernel⟩, ⟨1354, by decide +kernel⟩),
  (⟨1351, by decide +kernel⟩, ⟨1359, by decide +kernel⟩),
  (⟨1352, by decide +kernel⟩, ⟨857, by decide +kernel⟩)
]
def edgeBlock49 : List (Fin 1864 × Fin 1864) := [
  (⟨1352, by decide +kernel⟩, ⟨864, by decide +kernel⟩),
  (⟨1352, by decide +kernel⟩, ⟨1348, by decide +kernel⟩),
  (⟨1352, by decide +kernel⟩, ⟨1350, by decide +kernel⟩),
  (⟨1352, by decide +kernel⟩, ⟨1356, by decide +kernel⟩),
  (⟨1352, by decide +kernel⟩, ⟨1358, by decide +kernel⟩),
  (⟨1352, by decide +kernel⟩, ⟨1361, by decide +kernel⟩),
  (⟨1352, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1354, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1354, by decide +kernel⟩, ⟨1348, by decide +kernel⟩),
  (⟨1354, by decide +kernel⟩, ⟨1350, by decide +kernel⟩),
  (⟨1354, by decide +kernel⟩, ⟨1352, by decide +kernel⟩),
  (⟨1354, by decide +kernel⟩, ⟨1353, by decide +kernel⟩),
  (⟨1354, by decide +kernel⟩, ⟨1355, by decide +kernel⟩),
  (⟨1354, by decide +kernel⟩, ⟨1356, by decide +kernel⟩),
  (⟨1354, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1357, by decide +kernel⟩, ⟨1353, by decide +kernel⟩),
  (⟨1357, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1358, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1358, by decide +kernel⟩, ⟨1353, by decide +kernel⟩),
  (⟨1358, by decide +kernel⟩, ⟨1355, by decide +kernel⟩),
  (⟨1358, by decide +kernel⟩, ⟨1356, by decide +kernel⟩),
  (⟨1358, by decide +kernel⟩, ⟨1357, by decide +kernel⟩),
  (⟨1358, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1359, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1359, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1359, by decide +kernel⟩, ⟨1355, by decide +kernel⟩),
  (⟨1359, by decide +kernel⟩, ⟨1356, by decide +kernel⟩),
  (⟨1359, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1361, by decide +kernel⟩, ⟨864, by decide +kernel⟩),
  (⟨1361, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1361, by decide +kernel⟩, ⟨1356, by decide +kernel⟩),
  (⟨1361, by decide +kernel⟩, ⟨1357, by decide +kernel⟩),
  (⟨1362, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1362, by decide +kernel⟩, ⟨1365, by decide +kernel⟩),
  (⟨1364, by decide +kernel⟩, ⟨1369, by decide +kernel⟩),
  (⟨1373, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1373, by decide +kernel⟩, ⟨1630, by decide +kernel⟩),
  (⟨1373, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1374, by decide +kernel⟩, ⟨703, by decide +kernel⟩),
  (⟨1374, by decide +kernel⟩, ⟨704, by decide +kernel⟩),
  (⟨1377, by decide +kernel⟩, ⟨1376, by decide +kernel⟩),
  (⟨1377, by decide +kernel⟩, ⟨1385, by decide +kernel⟩),
  (⟨1378, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1378, by decide +kernel⟩, ⟨1233, by decide +kernel⟩),
  (⟨1378, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1378, by decide +kernel⟩, ⟨1376, by decide +kernel⟩),
  (⟨1378, by decide +kernel⟩, ⟨1385, by decide +kernel⟩),
  (⟨1379, by decide +kernel⟩, ⟨1232, by decide +kernel⟩),
  (⟨1379, by decide +kernel⟩, ⟨1376, by decide +kernel⟩),
  (⟨1379, by decide +kernel⟩, ⟨1377, by decide +kernel⟩),
  (⟨1379, by decide +kernel⟩, ⟨1378, by decide +kernel⟩),
  (⟨1379, by decide +kernel⟩, ⟨1380, by decide +kernel⟩),
  (⟨1379, by decide +kernel⟩, ⟨1381, by decide +kernel⟩),
  (⟨1379, by decide +kernel⟩, ⟨1382, by decide +kernel⟩),
  (⟨1379, by decide +kernel⟩, ⟨1383, by decide +kernel⟩),
  (⟨1379, by decide +kernel⟩, ⟨1384, by decide +kernel⟩),
  (⟨1380, by decide +kernel⟩, ⟨1376, by decide +kernel⟩),
  (⟨1380, by decide +kernel⟩, ⟨1385, by decide +kernel⟩),
  (⟨1381, by decide +kernel⟩, ⟨1376, by decide +kernel⟩),
  (⟨1381, by decide +kernel⟩, ⟨1385, by decide +kernel⟩),
  (⟨1382, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1382, by decide +kernel⟩, ⟨1376, by decide +kernel⟩),
  (⟨1383, by decide +kernel⟩, ⟨1376, by decide +kernel⟩),
  (⟨1383, by decide +kernel⟩, ⟨1385, by decide +kernel⟩)
]
def edgeBlock50 : List (Fin 1864 × Fin 1864) := [
  (⟨1384, by decide +kernel⟩, ⟨1376, by decide +kernel⟩),
  (⟨1384, by decide +kernel⟩, ⟨1385, by decide +kernel⟩),
  (⟨1385, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1385, by decide +kernel⟩, ⟨1376, by decide +kernel⟩),
  (⟨1386, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1387, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1387, by decide +kernel⟩, ⟨1536, by decide +kernel⟩),
  (⟨1387, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1389, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1391, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1392, by decide +kernel⟩, ⟨1640, by decide +kernel⟩),
  (⟨1392, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1393, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1393, by decide +kernel⟩, ⟨1406, by decide +kernel⟩),
  (⟨1393, by decide +kernel⟩, ⟨1457, by decide +kernel⟩),
  (⟨1393, by decide +kernel⟩, ⟨1458, by decide +kernel⟩),
  (⟨1393, by decide +kernel⟩, ⟨1560, by decide +kernel⟩),
  (⟨1393, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1396, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1396, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1396, by decide +kernel⟩, ⟨1118, by decide +kernel⟩),
  (⟨1396, by decide +kernel⟩, ⟨1134, by decide +kernel⟩),
  (⟨1396, by decide +kernel⟩, ⟨1218, by decide +kernel⟩),
  (⟨1397, by decide +kernel⟩, ⟨1396, by decide +kernel⟩),
  (⟨1397, by decide +kernel⟩, ⟨1398, by decide +kernel⟩),
  (⟨1397, by decide +kernel⟩, ⟨1399, by decide +kernel⟩),
  (⟨1397, by decide +kernel⟩, ⟨1401, by decide +kernel⟩),
  (⟨1397, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1398, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1398, by decide +kernel⟩, ⟨1220, by decide +kernel⟩),
  (⟨1398, by decide +kernel⟩, ⟨1396, by decide +kernel⟩),
  (⟨1398, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1399, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1399, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1399, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1399, by decide +kernel⟩, ⟨1396, by decide +kernel⟩),
  (⟨1400, by decide +kernel⟩, ⟨1396, by decide +kernel⟩),
  (⟨1400, by decide +kernel⟩, ⟨1399, by decide +kernel⟩),
  (⟨1401, by decide +kernel⟩, ⟨1396, by decide +kernel⟩),
  (⟨1402, by decide +kernel⟩, ⟨802, by decide +kernel⟩),
  (⟨1402, by decide +kernel⟩, ⟨988, by decide +kernel⟩),
  (⟨1403, by decide +kernel⟩, ⟨1574, by decide +kernel⟩),
  (⟨1404, by decide +kernel⟩, ⟨976, by decide +kernel⟩),
  (⟨1405, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1405, by decide +kernel⟩, ⟨1406, by decide +kernel⟩),
  (⟨1405, by decide +kernel⟩, ⟨1463, by decide +kernel⟩),
  (⟨1405, by decide +kernel⟩, ⟨1464, by decide +kernel⟩),
  (⟨1405, by decide +kernel⟩, ⟨1513, by decide +kernel⟩),
  (⟨1405, by decide +kernel⟩, ⟨1557, by decide +kernel⟩),
  (⟨1405, by decide +kernel⟩, ⟨1630, by decide +kernel⟩),
  (⟨1406, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1406, by decide +kernel⟩, ⟨988, by decide +kernel⟩),
  (⟨1406, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1406, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1406, by decide +kernel⟩, ⟨1396, by decide +kernel⟩),
  (⟨1406, by decide +kernel⟩, ⟨1457, by decide +kernel⟩),
  (⟨1406, by decide +kernel⟩, ⟨1458, by decide +kernel⟩),
  (⟨1406, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1407, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1409, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1409, by decide +kernel⟩, ⟨1758, by decide +kernel⟩),
  (⟨1410, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1410, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1410, by decide +kernel⟩, ⟨995, by decide +kernel⟩)
]
def edgeBlock51 : List (Fin 1864 × Fin 1864) := [
  (⟨1410, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1411, by decide +kernel⟩, ⟨993, by decide +kernel⟩),
  (⟨1412, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1412, by decide +kernel⟩, ⟨965, by decide +kernel⟩),
  (⟨1412, by decide +kernel⟩, ⟨977, by decide +kernel⟩),
  (⟨1412, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1412, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1412, by decide +kernel⟩, ⟨1435, by decide +kernel⟩),
  (⟨1412, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1412, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1415, by decide +kernel⟩, ⟨1061, by decide +kernel⟩),
  (⟨1415, by decide +kernel⟩, ⟨1062, by decide +kernel⟩),
  (⟨1415, by decide +kernel⟩, ⟨1416, by decide +kernel⟩),
  (⟨1416, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1416, by decide +kernel⟩, ⟨1062, by decide +kernel⟩),
  (⟨1418, by decide +kernel⟩, ⟨665, by decide +kernel⟩),
  (⟨1419, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1419, by decide +kernel⟩, ⟨1424, by decide +kernel⟩),
  (⟨1419, by decide +kernel⟩, ⟨1478, by decide +kernel⟩),
  (⟨1419, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1419, by decide +kernel⟩, ⟨1738, by decide +kernel⟩),
  (⟨1419, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1419, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1419, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1420, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1421, by decide +kernel⟩, ⟨1420, by decide +kernel⟩),
  (⟨1421, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1423, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1424, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1424, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1424, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1425, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1425, by decide +kernel⟩, ⟨1560, by decide +kernel⟩),
  (⟨1425, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1425, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1426, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1426, by decide +kernel⟩, ⟨1180, by decide +kernel⟩),
  (⟨1426, by decide +kernel⟩, ⟨1387, by decide +kernel⟩),
  (⟨1426, by decide +kernel⟩, ⟨1447, by decide +kernel⟩),
  (⟨1426, by decide +kernel⟩, ⟨1478, by decide +kernel⟩),
  (⟨1426, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1426, by decide +kernel⟩, ⟨1765, by decide +kernel⟩),
  (⟨1426, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1426, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1427, by decide +kernel⟩, ⟨1183, by decide +kernel⟩),
  (⟨1427, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1429, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1430, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1430, by decide +kernel⟩, ⟨1861, by decide +kernel⟩),
  (⟨1430, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1432, by decide +kernel⟩, ⟨1464, by decide +kernel⟩),
  (⟨1432, by decide +kernel⟩, ⟨1466, by decide +kernel⟩),
  (⟨1432, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1435, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1435, by decide +kernel⟩, ⟨1462, by decide +kernel⟩),
  (⟨1439, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1439, by decide +kernel⟩, ⟨988, by decide +kernel⟩),
  (⟨1439, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1439, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1439, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1440, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1441, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1441, by decide +kernel⟩, ⟨1093, by decide +kernel⟩),
  (⟨1441, by decide +kernel⟩, ⟨1108, by decide +kernel⟩)
]
def edgeBlock52 : List (Fin 1864 × Fin 1864) := [
  (⟨1441, by decide +kernel⟩, ⟨1457, by decide +kernel⟩),
  (⟨1441, by decide +kernel⟩, ⟨1706, by decide +kernel⟩),
  (⟨1441, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1443, by decide +kernel⟩, ⟨592, by decide +kernel⟩),
  (⟨1444, by decide +kernel⟩, ⟨988, by decide +kernel⟩),
  (⟨1444, by decide +kernel⟩, ⟨1130, by decide +kernel⟩),
  (⟨1444, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1444, by decide +kernel⟩, ⟨1148, by decide +kernel⟩),
  (⟨1444, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1444, by decide +kernel⟩, ⟨1185, by decide +kernel⟩),
  (⟨1444, by decide +kernel⟩, ⟨1209, by decide +kernel⟩),
  (⟨1444, by decide +kernel⟩, ⟨1216, by decide +kernel⟩),
  (⟨1445, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1446, by decide +kernel⟩, ⟨687, by decide +kernel⟩),
  (⟨1446, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1448, by decide +kernel⟩, ⟨1449, by decide +kernel⟩),
  (⟨1448, by decide +kernel⟩, ⟨1450, by decide +kernel⟩),
  (⟨1448, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨1448, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1450, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨1450, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1451, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1451, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1451, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1451, by decide +kernel⟩, ⟨1180, by decide +kernel⟩),
  (⟨1451, by decide +kernel⟩, ⟨1401, by decide +kernel⟩),
  (⟨1451, by decide +kernel⟩, ⟨1435, by decide +kernel⟩),
  (⟨1451, by decide +kernel⟩, ⟨1756, by decide +kernel⟩),
  (⟨1451, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1451, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1452, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1452, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1452, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1452, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1453, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1454, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1454, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1456, by decide +kernel⟩, ⟨1174, by decide +kernel⟩),
  (⟨1456, by decide +kernel⟩, ⟨1175, by decide +kernel⟩),
  (⟨1456, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1456, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1456, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1457, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1457, by decide +kernel⟩, ⟨1099, by decide +kernel⟩),
  (⟨1457, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1457, by decide +kernel⟩, ⟨1140, by decide +kernel⟩),
  (⟨1457, by decide +kernel⟩, ⟨1182, by decide +kernel⟩),
  (⟨1457, by decide +kernel⟩, ⟨1215, by decide +kernel⟩),
  (⟨1457, by decide +kernel⟩, ⟨1222, by decide +kernel⟩),
  (⟨1457, by decide +kernel⟩, ⟨1401, by decide +kernel⟩),
  (⟨1457, by decide +kernel⟩, ⟨1549, by decide +kernel⟩),
  (⟨1457, by decide +kernel⟩, ⟨1550, by decide +kernel⟩),
  (⟨1457, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1457, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1458, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1458, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1458, by decide +kernel⟩, ⟨1092, by decide +kernel⟩),
  (⟨1458, by decide +kernel⟩, ⟨1095, by decide +kernel⟩),
  (⟨1458, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1458, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1458, by decide +kernel⟩, ⟨1164, by decide +kernel⟩),
  (⟨1458, by decide +kernel⟩, ⟨1172, by decide +kernel⟩),
  (⟨1458, by decide +kernel⟩, ⟨1401, by decide +kernel⟩),
  (⟨1458, by decide +kernel⟩, ⟨1661, by decide +kernel⟩)
]
def edgeBlock53 : List (Fin 1864 × Fin 1864) := [
  (⟨1458, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1459, by decide +kernel⟩, ⟨973, by decide +kernel⟩),
  (⟨1459, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1462, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1463, by decide +kernel⟩, ⟨1461, by decide +kernel⟩),
  (⟨1463, by decide +kernel⟩, ⟨1464, by decide +kernel⟩),
  (⟨1463, by decide +kernel⟩, ⟨1466, by decide +kernel⟩),
  (⟨1463, by decide +kernel⟩, ⟨1472, by decide +kernel⟩),
  (⟨1463, by decide +kernel⟩, ⟨1473, by decide +kernel⟩),
  (⟨1463, by decide +kernel⟩, ⟨1615, by decide +kernel⟩),
  (⟨1464, by decide +kernel⟩, ⟨972, by decide +kernel⟩),
  (⟨1465, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1465, by decide +kernel⟩, ⟨972, by decide +kernel⟩),
  (⟨1466, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1466, by decide +kernel⟩, ⟨973, by decide +kernel⟩),
  (⟨1466, by decide +kernel⟩, ⟨1396, by decide +kernel⟩),
  (⟨1466, by decide +kernel⟩, ⟨1401, by decide +kernel⟩),
  (⟨1466, by decide +kernel⟩, ⟨1460, by decide +kernel⟩),
  (⟨1466, by decide +kernel⟩, ⟨1461, by decide +kernel⟩),
  (⟨1466, by decide +kernel⟩, ⟨1464, by decide +kernel⟩),
  (⟨1466, by decide +kernel⟩, ⟨1465, by decide +kernel⟩),
  (⟨1466, by decide +kernel⟩, ⟨1467, by decide +kernel⟩),
  (⟨1466, by decide +kernel⟩, ⟨1468, by decide +kernel⟩),
  (⟨1466, by decide +kernel⟩, ⟨1472, by decide +kernel⟩),
  (⟨1466, by decide +kernel⟩, ⟨1473, by decide +kernel⟩),
  (⟨1466, by decide +kernel⟩, ⟨1615, by decide +kernel⟩),
  (⟨1468, by decide +kernel⟩, ⟨1464, by decide +kernel⟩),
  (⟨1469, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1469, by decide +kernel⟩, ⟨1462, by decide +kernel⟩),
  (⟨1469, by decide +kernel⟩, ⟨1463, by decide +kernel⟩),
  (⟨1469, by decide +kernel⟩, ⟨1464, by decide +kernel⟩),
  (⟨1469, by decide +kernel⟩, ⟨1466, by decide +kernel⟩),
  (⟨1469, by decide +kernel⟩, ⟨1471, by decide +kernel⟩),
  (⟨1469, by decide +kernel⟩, ⟨1472, by decide +kernel⟩),
  (⟨1469, by decide +kernel⟩, ⟨1473, by decide +kernel⟩),
  (⟨1470, by decide +kernel⟩, ⟨1463, by decide +kernel⟩),
  (⟨1471, by decide +kernel⟩, ⟨1464, by decide +kernel⟩),
  (⟨1471, by decide +kernel⟩, ⟨1470, by decide +kernel⟩),
  (⟨1471, by decide +kernel⟩, ⟨1473, by decide +kernel⟩),
  (⟨1473, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1474, by decide +kernel⟩, ⟨690, by decide +kernel⟩),
  (⟨1474, by decide +kernel⟩, ⟨972, by decide +kernel⟩),
  (⟨1474, by decide +kernel⟩, ⟨973, by decide +kernel⟩),
  (⟨1474, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1474, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1474, by decide +kernel⟩, ⟨1396, by decide +kernel⟩),
  (⟨1474, by decide +kernel⟩, ⟨1400, by decide +kernel⟩),
  (⟨1474, by decide +kernel⟩, ⟨1401, by decide +kernel⟩),
  (⟨1474, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1474, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1476, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1476, by decide +kernel⟩, ⟨1615, by decide +kernel⟩),
  (⟨1477, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1479, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1479, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1480, by decide +kernel⟩, ⟨1588, by decide +kernel⟩),
  (⟨1480, by decide +kernel⟩, ⟨1637, by decide +kernel⟩),
  (⟨1480, by decide +kernel⟩, ⟨1640, by decide +kernel⟩),
  (⟨1484, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨63, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨66, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨967, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨968, by decide +kernel⟩)
]
def edgeBlock54 : List (Fin 1864 × Fin 1864) := [
  (⟨1485, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1102, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1105, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1114, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1145, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1164, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1200, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1205, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1219, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1301, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1318, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1319, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1367, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1396, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1398, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1411, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1413, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1417, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1426, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1433, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1438, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1439, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1441, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1447, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1450, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1451, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1454, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1457, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1481, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1486, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1487, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1488, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1490, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1492, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1493, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1495, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1496, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1497, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1500, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1501, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1502, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1514, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1525, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1543, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1549, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1575, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1578, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1579, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1582, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1583, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1595, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1599, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1603, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1642, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1644, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1689, by decide +kernel⟩)
]
def edgeBlock55 : List (Fin 1864 × Fin 1864) := [
  (⟨1485, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1691, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1695, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1718, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1721, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1761, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1762, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1768, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1793, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1795, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1826, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1485, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1486, by decide +kernel⟩, ⟨1433, by decide +kernel⟩),
  (⟨1486, by decide +kernel⟩, ⟨1482, by decide +kernel⟩),
  (⟨1486, by decide +kernel⟩, ⟨1643, by decide +kernel⟩),
  (⟨1487, by decide +kernel⟩, ⟨1174, by decide +kernel⟩),
  (⟨1487, by decide +kernel⟩, ⟨1226, by decide +kernel⟩),
  (⟨1487, by decide +kernel⟩, ⟨1483, by decide +kernel⟩),
  (⟨1487, by decide +kernel⟩, ⟨1616, by decide +kernel⟩),
  (⟨1487, by decide +kernel⟩, ⟨1618, by decide +kernel⟩),
  (⟨1488, by decide +kernel⟩, ⟨1174, by decide +kernel⟩),
  (⟨1488, by decide +kernel⟩, ⟨1226, by decide +kernel⟩),
  (⟨1488, by decide +kernel⟩, ⟨1375, by decide +kernel⟩),
  (⟨1488, by decide +kernel⟩, ⟨1487, by decide +kernel⟩),
  (⟨1488, by decide +kernel⟩, ⟨1498, by decide +kernel⟩),
  (⟨1488, by decide +kernel⟩, ⟨1644, by decide +kernel⟩),
  (⟨1488, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1489, by decide +kernel⟩, ⟨65, by decide +kernel⟩),
  (⟨1489, by decide +kernel⟩, ⟨1318, by decide +kernel⟩),
  (⟨1489, by decide +kernel⟩, ⟨1781, by decide +kernel⟩),
  (⟨1489, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1491, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1494, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1494, by decide +kernel⟩, ⟨1102, by decide +kernel⟩),
  (⟨1494, by decide +kernel⟩, ⟨1105, by decide +kernel⟩),
  (⟨1494, by decide +kernel⟩, ⟨1113, by decide +kernel⟩),
  (⟨1494, by decide +kernel⟩, ⟨1138, by decide +kernel⟩),
  (⟨1494, by decide +kernel⟩, ⟨1140, by decide +kernel⟩),
  (⟨1494, by decide +kernel⟩, ⟨1180, by decide +kernel⟩),
  (⟨1494, by decide +kernel⟩, ⟨1226, by decide +kernel⟩),
  (⟨1494, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨80, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1105, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1174, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1200, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1205, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1222, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1226, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1318, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1375, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1398, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1486, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1487, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1488, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1489, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1490, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1491, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1492, by decide +kernel⟩)
]
def edgeBlock56 : List (Fin 1864 × Fin 1864) := [
  (⟨1495, by decide +kernel⟩, ⟨1494, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1498, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1499, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1500, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1501, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1503, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1514, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1525, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1549, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1579, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1584, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1642, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1644, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1689, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1768, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1793, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1495, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1496, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1502, by decide +kernel⟩, ⟨1340, by decide +kernel⟩),
  (⟨1502, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1502, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1502, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨1503, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1503, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨1504, by decide +kernel⟩, ⟨1301, by decide +kernel⟩),
  (⟨1504, by decide +kernel⟩, ⟨1311, by decide +kernel⟩),
  (⟨1504, by decide +kernel⟩, ⟨1312, by decide +kernel⟩),
  (⟨1504, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨1504, by decide +kernel⟩, ⟨1318, by decide +kernel⟩),
  (⟨1504, by decide +kernel⟩, ⟨1330, by decide +kernel⟩),
  (⟨1505, by decide +kernel⟩, ⟨1046, by decide +kernel⟩),
  (⟨1505, by decide +kernel⟩, ⟨1615, by decide +kernel⟩),
  (⟨1506, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1507, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1507, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1508, by decide +kernel⟩, ⟨1053, by decide +kernel⟩),
  (⟨1509, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1510, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1511, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1511, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1511, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1512, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1512, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨1512, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1512, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1513, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1513, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1513, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1513, by decide +kernel⟩, ⟨1396, by decide +kernel⟩),
  (⟨1513, by decide +kernel⟩, ⟨1473, by decide +kernel⟩),
  (⟨1517, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨1517, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨63, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨66, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨73, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨80, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1447, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1515, by decide +kernel⟩)
]
def edgeBlock57 : List (Fin 1864 × Fin 1864) := [
  (⟨1520, by decide +kernel⟩, ⟨1516, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1518, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1519, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1523, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1524, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1526, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1527, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1529, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1646, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1758, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1788, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1789, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1790, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1793, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1826, by decide +kernel⟩),
  (⟨1520, by decide +kernel⟩, ⟨1831, by decide +kernel⟩),
  (⟨1523, by decide +kernel⟩, ⟨1524, by decide +kernel⟩),
  (⟨1526, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1526, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1527, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1527, by decide +kernel⟩, ⟨1295, by decide +kernel⟩),
  (⟨1527, by decide +kernel⟩, ⟨1299, by decide +kernel⟩),
  (⟨1527, by decide +kernel⟩, ⟨1300, by decide +kernel⟩),
  (⟨1527, by decide +kernel⟩, ⟨1314, by decide +kernel⟩),
  (⟨1527, by decide +kernel⟩, ⟨1318, by decide +kernel⟩),
  (⟨1527, by decide +kernel⟩, ⟨1324, by decide +kernel⟩),
  (⟨1527, by decide +kernel⟩, ⟨1333, by decide +kernel⟩),
  (⟨1527, by decide +kernel⟩, ⟨1344, by decide +kernel⟩),
  (⟨1527, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1527, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨1528, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1528, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1531, by decide +kernel⟩, ⟨1532, by decide +kernel⟩),
  (⟨1531, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1534, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨1534, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1534, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1534, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1534, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1536, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1537, by decide +kernel⟩, ⟨670, by decide +kernel⟩),
  (⟨1537, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1537, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1537, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1538, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1539, by decide +kernel⟩, ⟨1494, by decide +kernel⟩),
  (⟨1539, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1540, by decide +kernel⟩, ⟨1148, by decide +kernel⟩),
  (⟨1540, by decide +kernel⟩, ⟨1222, by decide +kernel⟩),
  (⟨1543, by decide +kernel⟩, ⟨1542, by decide +kernel⟩),
  (⟨1544, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1544, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1547, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1547, by decide +kernel⟩, ⟨1623, by decide +kernel⟩),
  (⟨1547, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1547, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1549, by decide +kernel⟩, ⟨1180, by decide +kernel⟩),
  (⟨1549, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1551, by decide +kernel⟩, ⟨967, by decide +kernel⟩),
  (⟨1551, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1551, by decide +kernel⟩, ⟨1139, by decide +kernel⟩),
  (⟨1551, by decide +kernel⟩, ⟨1141, by decide +kernel⟩),
  (⟨1551, by decide +kernel⟩, ⟨1145, by decide +kernel⟩)
]
def edgeBlock58 : List (Fin 1864 × Fin 1864) := [
  (⟨1551, by decide +kernel⟩, ⟨1160, by decide +kernel⟩),
  (⟨1551, by decide +kernel⟩, ⟨1182, by decide +kernel⟩),
  (⟨1551, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1551, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1552, by decide +kernel⟩, ⟨967, by decide +kernel⟩),
  (⟨1552, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1552, by decide +kernel⟩, ⟨1218, by decide +kernel⟩),
  (⟨1552, by decide +kernel⟩, ⟨1219, by decide +kernel⟩),
  (⟨1552, by decide +kernel⟩, ⟨1222, by decide +kernel⟩),
  (⟨1552, by decide +kernel⟩, ⟨1223, by decide +kernel⟩),
  (⟨1552, by decide +kernel⟩, ⟨1551, by decide +kernel⟩),
  (⟨1552, by decide +kernel⟩, ⟨1861, by decide +kernel⟩),
  (⟨1554, by decide +kernel⟩, ⟨1218, by decide +kernel⟩),
  (⟨1554, by decide +kernel⟩, ⟨1223, by decide +kernel⟩),
  (⟨1554, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1555, by decide +kernel⟩, ⟨1220, by decide +kernel⟩),
  (⟨1555, by decide +kernel⟩, ⟨1544, by decide +kernel⟩),
  (⟨1555, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1560, by decide +kernel⟩, ⟨979, by decide +kernel⟩),
  (⟨1560, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1560, by decide +kernel⟩, ⟨1065, by decide +kernel⟩),
  (⟨1560, by decide +kernel⟩, ⟨1174, by decide +kernel⟩),
  (⟨1560, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨1560, by decide +kernel⟩, ⟨1559, by decide +kernel⟩),
  (⟨1560, by decide +kernel⟩, ⟨1561, by decide +kernel⟩),
  (⟨1560, by decide +kernel⟩, ⟨1563, by decide +kernel⟩),
  (⟨1560, by decide +kernel⟩, ⟨1636, by decide +kernel⟩),
  (⟨1560, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1560, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1560, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1562, by decide +kernel⟩, ⟨1560, by decide +kernel⟩),
  (⟨1562, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1564, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1565, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1565, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1567, by decide +kernel⟩, ⟨897, by decide +kernel⟩),
  (⟨1567, by decide +kernel⟩, ⟨900, by decide +kernel⟩),
  (⟨1567, by decide +kernel⟩, ⟨903, by decide +kernel⟩),
  (⟨1567, by decide +kernel⟩, ⟨904, by decide +kernel⟩),
  (⟨1567, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨1567, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1568, by decide +kernel⟩, ⟨902, by decide +kernel⟩),
  (⟨1568, by decide +kernel⟩, ⟨903, by decide +kernel⟩),
  (⟨1568, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨1568, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1569, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1569, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1569, by decide +kernel⟩, ⟨1084, by decide +kernel⟩),
  (⟨1570, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1571, by decide +kernel⟩, ⟨880, by decide +kernel⟩),
  (⟨1571, by decide +kernel⟩, ⟨903, by decide +kernel⟩),
  (⟨1571, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨1571, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1571, by decide +kernel⟩, ⟨1565, by decide +kernel⟩),
  (⟨1572, by decide +kernel⟩, ⟨880, by decide +kernel⟩),
  (⟨1572, by decide +kernel⟩, ⟨903, by decide +kernel⟩),
  (⟨1572, by decide +kernel⟩, ⟨917, by decide +kernel⟩),
  (⟨1572, by decide +kernel⟩, ⟨996, by decide +kernel⟩),
  (⟨1572, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1572, by decide +kernel⟩, ⟨1571, by decide +kernel⟩),
  (⟨1573, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1574, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1574, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1574, by decide +kernel⟩, ⟨1401, by decide +kernel⟩)
]
def edgeBlock59 : List (Fin 1864 × Fin 1864) := [
  (⟨1574, by decide +kernel⟩, ⟨1473, by decide +kernel⟩),
  (⟨1574, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1576, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1577, by decide +kernel⟩, ⟨849, by decide +kernel⟩),
  (⟨1577, by decide +kernel⟩, ⟨864, by decide +kernel⟩),
  (⟨1577, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1577, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1577, by decide +kernel⟩, ⟨1365, by decide +kernel⟩),
  (⟨1579, by decide +kernel⟩, ⟨1389, by decide +kernel⟩),
  (⟨1579, by decide +kernel⟩, ⟨1401, by decide +kernel⟩),
  (⟨1579, by decide +kernel⟩, ⟨1574, by decide +kernel⟩),
  (⟨1579, by decide +kernel⟩, ⟨1575, by decide +kernel⟩),
  (⟨1579, by decide +kernel⟩, ⟨1576, by decide +kernel⟩),
  (⟨1579, by decide +kernel⟩, ⟨1577, by decide +kernel⟩),
  (⟨1579, by decide +kernel⟩, ⟨1578, by decide +kernel⟩),
  (⟨1579, by decide +kernel⟩, ⟨1580, by decide +kernel⟩),
  (⟨1582, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1105, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1144, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1174, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1200, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1205, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1215, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1218, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1222, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1223, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1225, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1226, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1318, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1392, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1456, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1457, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1479, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1487, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1502, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1534, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1546, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1549, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1578, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1582, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1584, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1585, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1586, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1587, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1589, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1600, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1614, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1615, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1583, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1586, by decide +kernel⟩, ⟨968, by decide +kernel⟩),
  (⟨1586, by decide +kernel⟩, ⟨1218, by decide +kernel⟩),
  (⟨1586, by decide +kernel⟩, ⟨1220, by decide +kernel⟩),
  (⟨1586, by decide +kernel⟩, ⟨1223, by decide +kernel⟩),
  (⟨1586, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1590, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1590, by decide +kernel⟩, ⟨995, by decide +kernel⟩)
]
def edgeBlock60 : List (Fin 1864 × Fin 1864) := [
  (⟨1590, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1590, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1591, by decide +kernel⟩, ⟨1590, by decide +kernel⟩),
  (⟨1591, by decide +kernel⟩, ⟨1615, by decide +kernel⟩),
  (⟨1592, by decide +kernel⟩, ⟨1232, by decide +kernel⟩),
  (⟨1592, by decide +kernel⟩, ⟨1593, by decide +kernel⟩),
  (⟨1593, by decide +kernel⟩, ⟨1385, by decide +kernel⟩),
  (⟨1595, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1596, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1598, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1599, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1600, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1600, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1600, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨1600, by decide +kernel⟩, ⟨1488, by decide +kernel⟩),
  (⟨1600, by decide +kernel⟩, ⟨1495, by decide +kernel⟩),
  (⟨1600, by decide +kernel⟩, ⟨1502, by decide +kernel⟩),
  (⟨1600, by decide +kernel⟩, ⟨1589, by decide +kernel⟩),
  (⟨1600, by decide +kernel⟩, ⟨1601, by decide +kernel⟩),
  (⟨1600, by decide +kernel⟩, ⟨1634, by decide +kernel⟩),
  (⟨1600, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1600, by decide +kernel⟩, ⟨1710, by decide +kernel⟩),
  (⟨1600, by decide +kernel⟩, ⟨1770, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨80, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨993, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨1318, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨1451, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨1491, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨1503, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨1517, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨1529, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨1717, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨1718, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨1720, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨1756, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨1762, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨1767, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1603, by decide +kernel⟩, ⟨1826, by decide +kernel⟩),
  (⟨1604, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1604, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1604, by decide +kernel⟩, ⟨1180, by decide +kernel⟩),
  (⟨1604, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1604, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1605, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1606, by decide +kernel⟩, ⟨665, by decide +kernel⟩),
  (⟨1606, by decide +kernel⟩, ⟨1607, by decide +kernel⟩),
  (⟨1606, by decide +kernel⟩, ⟨1608, by decide +kernel⟩),
  (⟨1606, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1607, by decide +kernel⟩, ⟨665, by decide +kernel⟩),
  (⟨1607, by decide +kernel⟩, ⟨1608, by decide +kernel⟩),
  (⟨1608, by decide +kernel⟩, ⟨665, by decide +kernel⟩),
  (⟨1608, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1608, by decide +kernel⟩, ⟨1609, by decide +kernel⟩),
  (⟨1608, by decide +kernel⟩, ⟨1704, by decide +kernel⟩),
  (⟨1608, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1608, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1609, by decide +kernel⟩, ⟨1704, by decide +kernel⟩),
  (⟨1610, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1612, by decide +kernel⟩, ⟨584, by decide +kernel⟩),
  (⟨1612, by decide +kernel⟩, ⟨1611, by decide +kernel⟩),
  (⟨1613, by decide +kernel⟩, ⟨967, by decide +kernel⟩),
  (⟨1613, by decide +kernel⟩, ⟨1690, by decide +kernel⟩)
]
def edgeBlock61 : List (Fin 1864 × Fin 1864) := [
  (⟨1614, by decide +kernel⟩, ⟨1615, by decide +kernel⟩),
  (⟨1614, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1614, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1620, by decide +kernel⟩, ⟨928, by decide +kernel⟩),
  (⟨1620, by decide +kernel⟩, ⟨930, by decide +kernel⟩),
  (⟨1620, by decide +kernel⟩, ⟨1084, by decide +kernel⟩),
  (⟨1620, by decide +kernel⟩, ⟨1329, by decide +kernel⟩),
  (⟨1620, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1622, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1622, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1623, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1624, by decide +kernel⟩, ⟨1549, by decide +kernel⟩),
  (⟨1624, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1624, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1625, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1626, by decide +kernel⟩, ⟨1396, by decide +kernel⟩),
  (⟨1626, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1627, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1627, by decide +kernel⟩, ⟨1628, by decide +kernel⟩),
  (⟨1627, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1629, by decide +kernel⟩, ⟨1630, by decide +kernel⟩),
  (⟨1631, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1631, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1632, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1632, by decide +kernel⟩, ⟨1738, by decide +kernel⟩),
  (⟨1632, by decide +kernel⟩, ⟨1740, by decide +kernel⟩),
  (⟨1632, by decide +kernel⟩, ⟨1742, by decide +kernel⟩),
  (⟨1632, by decide +kernel⟩, ⟨1744, by decide +kernel⟩),
  (⟨1632, by decide +kernel⟩, ⟨1745, by decide +kernel⟩),
  (⟨1632, by decide +kernel⟩, ⟨1747, by decide +kernel⟩),
  (⟨1632, by decide +kernel⟩, ⟨1750, by decide +kernel⟩),
  (⟨1632, by decide +kernel⟩, ⟨1751, by decide +kernel⟩),
  (⟨1632, by decide +kernel⟩, ⟨1752, by decide +kernel⟩),
  (⟨1632, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1633, by decide +kernel⟩, ⟨1634, by decide +kernel⟩),
  (⟨1634, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1634, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1634, by decide +kernel⟩, ⟨1611, by decide +kernel⟩),
  (⟨1634, by decide +kernel⟩, ⟨1612, by decide +kernel⟩),
  (⟨1634, by decide +kernel⟩, ⟨1698, by decide +kernel⟩),
  (⟨1634, by decide +kernel⟩, ⟨1791, by decide +kernel⟩),
  (⟨1634, by decide +kernel⟩, ⟨1807, by decide +kernel⟩),
  (⟨1635, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1635, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1640, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1642, by decide +kernel⟩, ⟨1641, by decide +kernel⟩),
  (⟨1642, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1645, by decide +kernel⟩, ⟨1105, by decide +kernel⟩),
  (⟨1647, by decide +kernel⟩, ⟨1066, by decide +kernel⟩),
  (⟨1647, by decide +kernel⟩, ⟨1067, by decide +kernel⟩),
  (⟨1648, by decide +kernel⟩, ⟨802, by decide +kernel⟩),
  (⟨1648, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1648, by decide +kernel⟩, ⟨1068, by decide +kernel⟩),
  (⟨1649, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1649, by decide +kernel⟩, ⟨1113, by decide +kernel⟩),
  (⟨1649, by decide +kernel⟩, ⟨1124, by decide +kernel⟩),
  (⟨1649, by decide +kernel⟩, ⟨1406, by decide +kernel⟩),
  (⟨1649, by decide +kernel⟩, ⟨1650, by decide +kernel⟩),
  (⟨1649, by decide +kernel⟩, ⟨1651, by decide +kernel⟩),
  (⟨1649, by decide +kernel⟩, ⟨1660, by decide +kernel⟩),
  (⟨1649, by decide +kernel⟩, ⟨1662, by decide +kernel⟩),
  (⟨1649, by decide +kernel⟩, ⟨1663, by decide +kernel⟩),
  (⟨1649, by decide +kernel⟩, ⟨1664, by decide +kernel⟩),
  (⟨1649, by decide +kernel⟩, ⟨1665, by decide +kernel⟩)
]
def edgeBlock62 : List (Fin 1864 × Fin 1864) := [
  (⟨1649, by decide +kernel⟩, ⟨1667, by decide +kernel⟩),
  (⟨1649, by decide +kernel⟩, ⟨1671, by decide +kernel⟩),
  (⟨1649, by decide +kernel⟩, ⟨1672, by decide +kernel⟩),
  (⟨1649, by decide +kernel⟩, ⟨1695, by decide +kernel⟩),
  (⟨1651, by decide +kernel⟩, ⟨1218, by decide +kernel⟩),
  (⟨1651, by decide +kernel⟩, ⟨1220, by decide +kernel⟩),
  (⟨1651, by decide +kernel⟩, ⟨1396, by decide +kernel⟩),
  (⟨1651, by decide +kernel⟩, ⟨1457, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1220, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1246, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1438, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1439, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1494, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1496, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1539, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1555, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1633, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1634, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1639, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1649, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1654, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1662, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1664, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1666, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1668, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1669, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1695, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1698, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1732, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1733, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1734, by decide +kernel⟩),
  (⟨1652, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨988, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1108, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1220, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1390, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1393, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1438, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1458, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1555, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1579, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1590, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1606, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1627, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1651, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1655, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1656, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1661, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1662, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1665, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1667, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1669, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1671, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1654, by decide +kernel⟩, ⟨1860, by decide +kernel⟩)
]
def edgeBlock63 : List (Fin 1864 × Fin 1864) := [
  (⟨1654, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1656, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1656, by decide +kernel⟩, ⟨1550, by decide +kernel⟩),
  (⟨1656, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1657, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1657, by decide +kernel⟩, ⟨1539, by decide +kernel⟩),
  (⟨1657, by decide +kernel⟩, ⟨1579, by decide +kernel⟩),
  (⟨1657, by decide +kernel⟩, ⟨1649, by decide +kernel⟩),
  (⟨1657, by decide +kernel⟩, ⟨1660, by decide +kernel⟩),
  (⟨1657, by decide +kernel⟩, ⟨1661, by decide +kernel⟩),
  (⟨1657, by decide +kernel⟩, ⟨1667, by decide +kernel⟩),
  (⟨1657, by decide +kernel⟩, ⟨1669, by decide +kernel⟩),
  (⟨1657, by decide +kernel⟩, ⟨1670, by decide +kernel⟩),
  (⟨1657, by decide +kernel⟩, ⟨1695, by decide +kernel⟩),
  (⟨1657, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1665, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1665, by decide +kernel⟩, ⟨1222, by decide +kernel⟩),
  (⟨1665, by decide +kernel⟩, ⟨1396, by decide +kernel⟩),
  (⟨1665, by decide +kernel⟩, ⟨1458, by decide +kernel⟩),
  (⟨1665, by decide +kernel⟩, ⟨1674, by decide +kernel⟩),
  (⟨1666, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1667, by decide +kernel⟩, ⟨1579, by decide +kernel⟩),
  (⟨1667, by decide +kernel⟩, ⟨1659, by decide +kernel⟩),
  (⟨1667, by decide +kernel⟩, ⟨1673, by decide +kernel⟩),
  (⟨1667, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1668, by decide +kernel⟩, ⟨1220, by decide +kernel⟩),
  (⟨1668, by decide +kernel⟩, ⟨1404, by decide +kernel⟩),
  (⟨1668, by decide +kernel⟩, ⟨1406, by decide +kernel⟩),
  (⟨1668, by decide +kernel⟩, ⟨1657, by decide +kernel⟩),
  (⟨1668, by decide +kernel⟩, ⟨1658, by decide +kernel⟩),
  (⟨1668, by decide +kernel⟩, ⟨1667, by decide +kernel⟩),
  (⟨1668, by decide +kernel⟩, ⟨1675, by decide +kernel⟩),
  (⟨1669, by decide +kernel⟩, ⟨1539, by decide +kernel⟩),
  (⟨1669, by decide +kernel⟩, ⟨1653, by decide +kernel⟩),
  (⟨1669, by decide +kernel⟩, ⟨1659, by decide +kernel⟩),
  (⟨1669, by decide +kernel⟩, ⟨1661, by decide +kernel⟩),
  (⟨1669, by decide +kernel⟩, ⟨1667, by decide +kernel⟩),
  (⟨1669, by decide +kernel⟩, ⟨1670, by decide +kernel⟩),
  (⟨1669, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1670, by decide +kernel⟩, ⟨1639, by decide +kernel⟩),
  (⟨1670, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1671, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1671, by decide +kernel⟩, ⟨1636, by decide +kernel⟩),
  (⟨1672, by decide +kernel⟩, ⟨1660, by decide +kernel⟩),
  (⟨1675, by decide +kernel⟩, ⟨1650, by decide +kernel⟩),
  (⟨1676, by decide +kernel⟩, ⟨1675, by decide +kernel⟩),
  (⟨1677, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1679, by decide +kernel⟩, ⟨1069, by decide +kernel⟩),
  (⟨1681, by decide +kernel⟩, ⟨1165, by decide +kernel⟩),
  (⟨1681, by decide +kernel⟩, ⟨1549, by decide +kernel⟩),
  (⟨1681, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1683, by decide +kernel⟩, ⟨967, by decide +kernel⟩),
  (⟨1683, by decide +kernel⟩, ⟨1398, by decide +kernel⟩),
  (⟨1683, by decide +kernel⟩, ⟨1403, by decide +kernel⟩),
  (⟨1683, by decide +kernel⟩, ⟨1406, by decide +kernel⟩),
  (⟨1683, by decide +kernel⟩, ⟨1463, by decide +kernel⟩),
  (⟨1683, by decide +kernel⟩, ⟨1464, by decide +kernel⟩),
  (⟨1683, by decide +kernel⟩, ⟨1513, by decide +kernel⟩),
  (⟨1683, by decide +kernel⟩, ⟨1557, by decide +kernel⟩),
  (⟨1683, by decide +kernel⟩, ⟨1726, by decide +kernel⟩),
  (⟨1685, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1685, by decide +kernel⟩, ⟨1186, by decide +kernel⟩),
  (⟨1685, by decide +kernel⟩, ⟨1684, by decide +kernel⟩),
  (⟨1685, by decide +kernel⟩, ⟨1860, by decide +kernel⟩)
]
def edgeBlock64 : List (Fin 1864 × Fin 1864) := [
  (⟨1687, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1687, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1688, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1689, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1689, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1689, by decide +kernel⟩, ⟨1145, by decide +kernel⟩),
  (⟨1689, by decide +kernel⟩, ⟨1188, by decide +kernel⟩),
  (⟨1689, by decide +kernel⟩, ⟨1457, by decide +kernel⟩),
  (⟨1689, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1690, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1690, by decide +kernel⟩, ⟨998, by decide +kernel⟩),
  (⟨1691, by decide +kernel⟩, ⟨1301, by decide +kernel⟩),
  (⟨1691, by decide +kernel⟩, ⟨1313, by decide +kernel⟩),
  (⟨1691, by decide +kernel⟩, ⟨1318, by decide +kernel⟩),
  (⟨1691, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1692, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1693, by decide +kernel⟩, ⟨1071, by decide +kernel⟩),
  (⟨1693, by decide +kernel⟩, ⟨1072, by decide +kernel⟩),
  (⟨1693, by decide +kernel⟩, ⟨1074, by decide +kernel⟩),
  (⟨1700, by decide +kernel⟩, ⟨1077, by decide +kernel⟩),
  (⟨1701, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1702, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1702, by decide +kernel⟩, ⟨1463, by decide +kernel⟩),
  (⟨1702, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1704, by decide +kernel⟩, ⟨665, by decide +kernel⟩),
  (⟨1704, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1704, by decide +kernel⟩, ⟨1430, by decide +kernel⟩),
  (⟨1704, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1704, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1705, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1707, by decide +kernel⟩, ⟨1457, by decide +kernel⟩),
  (⟨1708, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1708, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1708, by decide +kernel⟩, ⟨1430, by decide +kernel⟩),
  (⟨1708, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1708, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1709, by decide +kernel⟩, ⟨964, by decide +kernel⟩),
  (⟨1710, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1710, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1710, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨1710, by decide +kernel⟩, ⟨1433, by decide +kernel⟩),
  (⟨1710, by decide +kernel⟩, ⟨1434, by decide +kernel⟩),
  (⟨1710, by decide +kernel⟩, ⟨1699, by decide +kernel⟩),
  (⟨1710, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1711, by decide +kernel⟩, ⟨998, by decide +kernel⟩),
  (⟨1713, by decide +kernel⟩, ⟨990, by decide +kernel⟩),
  (⟨1713, by decide +kernel⟩, ⟨1401, by decide +kernel⟩),
  (⟨1713, by decide +kernel⟩, ⟨1712, by decide +kernel⟩),
  (⟨1713, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1714, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1714, by decide +kernel⟩, ⟨1140, by decide +kernel⟩),
  (⟨1714, by decide +kernel⟩, ⟨1196, by decide +kernel⟩),
  (⟨1714, by decide +kernel⟩, ⟨1228, by decide +kernel⟩),
  (⟨1714, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1715, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1715, by decide +kernel⟩, ⟨1227, by decide +kernel⟩),
  (⟨1715, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1717, by decide +kernel⟩, ⟨1437, by decide +kernel⟩),
  (⟨1717, by decide +kernel⟩, ⟨1782, by decide +kernel⟩),
  (⟨1717, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1718, by decide +kernel⟩, ⟨75, by decide +kernel⟩),
  (⟨1718, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1718, by decide +kernel⟩, ⟨993, by decide +kernel⟩),
  (⟨1718, by decide +kernel⟩, ⟨995, by decide +kernel⟩)
]
def edgeBlock65 : List (Fin 1864 × Fin 1864) := [
  (⟨1718, by decide +kernel⟩, ⟨1301, by decide +kernel⟩),
  (⟨1718, by decide +kernel⟩, ⟨1345, by decide +kernel⟩),
  (⟨1718, by decide +kernel⟩, ⟨1520, by decide +kernel⟩),
  (⟨1718, by decide +kernel⟩, ⟨1719, by decide +kernel⟩),
  (⟨1718, by decide +kernel⟩, ⟨1720, by decide +kernel⟩),
  (⟨1718, by decide +kernel⟩, ⟨1754, by decide +kernel⟩),
  (⟨1718, by decide +kernel⟩, ⟨1760, by decide +kernel⟩),
  (⟨1718, by decide +kernel⟩, ⟨1765, by decide +kernel⟩),
  (⟨1718, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1719, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1720, by decide +kernel⟩, ⟨65, by decide +kernel⟩),
  (⟨1720, by decide +kernel⟩, ⟨1318, by decide +kernel⟩),
  (⟨1720, by decide +kernel⟩, ⟨1558, by decide +kernel⟩),
  (⟨1720, by decide +kernel⟩, ⟨1559, by decide +kernel⟩),
  (⟨1720, by decide +kernel⟩, ⟨1769, by decide +kernel⟩),
  (⟨1720, by decide +kernel⟩, ⟨1781, by decide +kernel⟩),
  (⟨1720, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1721, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1113, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1398, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1404, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1480, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1494, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1496, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1539, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1555, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1649, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1657, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1722, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1732, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1734, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1723, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1724, by decide +kernel⟩, ⟨1576, by decide +kernel⟩),
  (⟨1725, by decide +kernel⟩, ⟨1695, by decide +kernel⟩),
  (⟨1725, by decide +kernel⟩, ⟨1727, by decide +kernel⟩),
  (⟨1725, by decide +kernel⟩, ⟨1728, by decide +kernel⟩),
  (⟨1726, by decide +kernel⟩, ⟨1398, by decide +kernel⟩),
  (⟨1726, by decide +kernel⟩, ⟨1539, by decide +kernel⟩),
  (⟨1726, by decide +kernel⟩, ⟨1576, by decide +kernel⟩),
  (⟨1726, by decide +kernel⟩, ⟨1725, by decide +kernel⟩),
  (⟨1726, by decide +kernel⟩, ⟨1727, by decide +kernel⟩),
  (⟨1726, by decide +kernel⟩, ⟨1731, by decide +kernel⟩),
  (⟨1728, by decide +kernel⟩, ⟨1200, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1404, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1475, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1494, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1496, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1555, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1633, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1634, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1649, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1657, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1685, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1690, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1698, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1724, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1730, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1731, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1733, by decide +kernel⟩),
  (⟨1729, by decide +kernel⟩, ⟨1734, by decide +kernel⟩)
]
def edgeBlock66 : List (Fin 1864 × Fin 1864) := [
  (⟨1729, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1730, by decide +kernel⟩, ⟨1439, by decide +kernel⟩),
  (⟨1730, by decide +kernel⟩, ⟨1695, by decide +kernel⟩),
  (⟨1730, by decide +kernel⟩, ⟨1728, by decide +kernel⟩),
  (⟨1731, by decide +kernel⟩, ⟨1105, by decide +kernel⟩),
  (⟨1731, by decide +kernel⟩, ⟨1174, by decide +kernel⟩),
  (⟨1731, by decide +kernel⟩, ⟨1539, by decide +kernel⟩),
  (⟨1731, by decide +kernel⟩, ⟨1645, by decide +kernel⟩),
  (⟨1731, by decide +kernel⟩, ⟨1735, by decide +kernel⟩),
  (⟨1731, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1732, by decide +kernel⟩, ⟨1555, by decide +kernel⟩),
  (⟨1734, by decide +kernel⟩, ⟨1218, by decide +kernel⟩),
  (⟨1734, by decide +kernel⟩, ⟨1223, by decide +kernel⟩),
  (⟨1735, by decide +kernel⟩, ⟨1127, by decide +kernel⟩),
  (⟨1735, by decide +kernel⟩, ⟨1639, by decide +kernel⟩),
  (⟨1736, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1736, by decide +kernel⟩, ⟨1404, by decide +kernel⟩),
  (⟨1736, by decide +kernel⟩, ⟨1439, by decide +kernel⟩),
  (⟨1736, by decide +kernel⟩, ⟨1537, by decide +kernel⟩),
  (⟨1736, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1736, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1740, by decide +kernel⟩, ⟨1738, by decide +kernel⟩),
  (⟨1740, by decide +kernel⟩, ⟨1750, by decide +kernel⟩),
  (⟨1740, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1741, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1741, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1741, by decide +kernel⟩, ⟨1826, by decide +kernel⟩),
  (⟨1741, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1742, by decide +kernel⟩, ⟨1738, by decide +kernel⟩),
  (⟨1742, by decide +kernel⟩, ⟨1743, by decide +kernel⟩),
  (⟨1743, by decide +kernel⟩, ⟨1738, by decide +kernel⟩),
  (⟨1744, by decide +kernel⟩, ⟨1747, by decide +kernel⟩),
  (⟨1744, by decide +kernel⟩, ⟨1750, by decide +kernel⟩),
  (⟨1746, by decide +kernel⟩, ⟨1738, by decide +kernel⟩),
  (⟨1746, by decide +kernel⟩, ⟨1747, by decide +kernel⟩),
  (⟨1747, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1747, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨1749, by decide +kernel⟩, ⟨1738, by decide +kernel⟩),
  (⟨1749, by decide +kernel⟩, ⟨1750, by decide +kernel⟩),
  (⟨1750, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1750, by decide +kernel⟩, ⟨1738, by decide +kernel⟩),
  (⟨1751, by decide +kernel⟩, ⟨1738, by decide +kernel⟩),
  (⟨1751, by decide +kernel⟩, ⟨1743, by decide +kernel⟩),
  (⟨1751, by decide +kernel⟩, ⟨1746, by decide +kernel⟩),
  (⟨1751, by decide +kernel⟩, ⟨1748, by decide +kernel⟩),
  (⟨1751, by decide +kernel⟩, ⟨1749, by decide +kernel⟩),
  (⟨1752, by decide +kernel⟩, ⟨1742, by decide +kernel⟩),
  (⟨1752, by decide +kernel⟩, ⟨1750, by decide +kernel⟩),
  (⟨1752, by decide +kernel⟩, ⟨1751, by decide +kernel⟩),
  (⟨1753, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1753, by decide +kernel⟩, ⟨1789, by decide +kernel⟩),
  (⟨1753, by decide +kernel⟩, ⟨1791, by decide +kernel⟩),
  (⟨1754, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1754, by decide +kernel⟩, ⟨1755, by decide +kernel⟩),
  (⟨1754, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1757, by decide +kernel⟩, ⟨1758, by decide +kernel⟩),
  (⟨1760, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1760, by decide +kernel⟩, ⟨993, by decide +kernel⟩),
  (⟨1760, by decide +kernel⟩, ⟨1758, by decide +kernel⟩),
  (⟨1760, by decide +kernel⟩, ⟨1761, by decide +kernel⟩),
  (⟨1760, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1760, by decide +kernel⟩, ⟨1826, by decide +kernel⟩),
  (⟨1762, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1762, by decide +kernel⟩, ⟨1826, by decide +kernel⟩)
]
def edgeBlock67 : List (Fin 1864 × Fin 1864) := [
  (⟨1772, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1772, by decide +kernel⟩, ⟨1805, by decide +kernel⟩),
  (⟨1773, by decide +kernel⟩, ⟨1368, by decide +kernel⟩),
  (⟨1773, by decide +kernel⟩, ⟨1779, by decide +kernel⟩),
  (⟨1774, by decide +kernel⟩, ⟨1777, by decide +kernel⟩),
  (⟨1774, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1777, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1778, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1778, by decide +kernel⟩, ⟨1369, by decide +kernel⟩),
  (⟨1778, by decide +kernel⟩, ⟨1775, by decide +kernel⟩),
  (⟨1778, by decide +kernel⟩, ⟨1777, by decide +kernel⟩),
  (⟨1778, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1778, by decide +kernel⟩, ⟨1801, by decide +kernel⟩),
  (⟨1778, by decide +kernel⟩, ⟨1812, by decide +kernel⟩),
  (⟨1780, by decide +kernel⟩, ⟨1782, by decide +kernel⟩),
  (⟨1780, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1780, by decide +kernel⟩, ⟨1805, by decide +kernel⟩),
  (⟨1781, by decide +kernel⟩, ⟨1780, by decide +kernel⟩),
  (⟨1781, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1788, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1788, by decide +kernel⟩, ⟨1789, by decide +kernel⟩),
  (⟨1788, by decide +kernel⟩, ⟨1791, by decide +kernel⟩),
  (⟨1788, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1788, by decide +kernel⟩, ⟨1831, by decide +kernel⟩),
  (⟨1790, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1792, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1792, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1795, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1796, by decide +kernel⟩, ⟨1795, by decide +kernel⟩),
  (⟨1798, by decide +kernel⟩, ⟨1815, by decide +kernel⟩),
  (⟨1799, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1802, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1802, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨1802, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1803, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1803, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1804, by decide +kernel⟩, ⟨1803, by decide +kernel⟩),
  (⟨1805, by decide +kernel⟩, ⟨1326, by decide +kernel⟩),
  (⟨1805, by decide +kernel⟩, ⟨1369, by decide +kernel⟩),
  (⟨1805, by decide +kernel⟩, ⟨1801, by decide +kernel⟩),
  (⟨1805, by decide +kernel⟩, ⟨1812, by decide +kernel⟩),
  (⟨1806, by decide +kernel⟩, ⟨1002, by decide +kernel⟩),
  (⟨1806, by decide +kernel⟩, ⟨1369, by decide +kernel⟩),
  (⟨1811, by decide +kernel⟩, ⟨1364, by decide +kernel⟩),
  (⟨1811, by decide +kernel⟩, ⟨1369, by decide +kernel⟩),
  (⟨1814, by decide +kernel⟩, ⟨1813, by decide +kernel⟩),
  (⟨1814, by decide +kernel⟩, ⟨1820, by decide +kernel⟩),
  (⟨1815, by decide +kernel⟩, ⟨991, by decide +kernel⟩),
  (⟨1815, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1819, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1819, by decide +kernel⟩, ⟨1800, by decide +kernel⟩),
  (⟨1820, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1821, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1823, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1824, by decide +kernel⟩, ⟨1798, by decide +kernel⟩),
  (⟨1824, by decide +kernel⟩, ⟨1820, by decide +kernel⟩),
  (⟨1824, by decide +kernel⟩, ⟨1821, by decide +kernel⟩),
  (⟨1824, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨1825, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1827, by decide +kernel⟩, ⟨1826, by decide +kernel⟩),
  (⟨1830, by decide +kernel⟩, ⟨1828, by decide +kernel⟩),
  (⟨1830, by decide +kernel⟩, ⟨1829, by decide +kernel⟩),
  (⟨1831, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1832, by decide +kernel⟩, ⟨995, by decide +kernel⟩)
]
def edgeBlock68 : List (Fin 1864 × Fin 1864) := [
  (⟨1832, by decide +kernel⟩, ⟨1362, by decide +kernel⟩),
  (⟨1832, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1832, by decide +kernel⟩, ⟨1797, by decide +kernel⟩),
  (⟨1833, by decide +kernel⟩, ⟨971, by decide +kernel⟩),
  (⟨1833, by decide +kernel⟩, ⟨974, by decide +kernel⟩),
  (⟨1833, by decide +kernel⟩, ⟨1773, by decide +kernel⟩),
  (⟨1833, by decide +kernel⟩, ⟨1774, by decide +kernel⟩),
  (⟨1833, by decide +kernel⟩, ⟨1775, by decide +kernel⟩),
  (⟨1833, by decide +kernel⟩, ⟨1777, by decide +kernel⟩),
  (⟨1833, by decide +kernel⟩, ⟨1778, by decide +kernel⟩),
  (⟨1833, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1833, by decide +kernel⟩, ⟨1797, by decide +kernel⟩),
  (⟨1833, by decide +kernel⟩, ⟨1832, by decide +kernel⟩),
  (⟨1835, by decide +kernel⟩, ⟨1834, by decide +kernel⟩),
  (⟨1836, by decide +kernel⟩, ⟨1000, by decide +kernel⟩),
  (⟨1836, by decide +kernel⟩, ⟨1326, by decide +kernel⟩),
  (⟨1836, by decide +kernel⟩, ⟨1367, by decide +kernel⟩),
  (⟨1836, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1836, by decide +kernel⟩, ⟨1797, by decide +kernel⟩),
  (⟨1836, by decide +kernel⟩, ⟨1801, by decide +kernel⟩),
  (⟨1836, by decide +kernel⟩, ⟨1808, by decide +kernel⟩),
  (⟨1836, by decide +kernel⟩, ⟨1810, by decide +kernel⟩),
  (⟨1836, by decide +kernel⟩, ⟨1811, by decide +kernel⟩),
  (⟨1836, by decide +kernel⟩, ⟨1822, by decide +kernel⟩),
  (⟨1836, by decide +kernel⟩, ⟨1837, by decide +kernel⟩),
  (⟨1836, by decide +kernel⟩, ⟨1839, by decide +kernel⟩),
  (⟨1837, by decide +kernel⟩, ⟨1367, by decide +kernel⟩),
  (⟨1837, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1837, by decide +kernel⟩, ⟨1801, by decide +kernel⟩),
  (⟨1837, by decide +kernel⟩, ⟨1810, by decide +kernel⟩),
  (⟨1837, by decide +kernel⟩, ⟨1811, by decide +kernel⟩),
  (⟨1837, by decide +kernel⟩, ⟨1816, by decide +kernel⟩),
  (⟨1837, by decide +kernel⟩, ⟨1817, by decide +kernel⟩),
  (⟨1837, by decide +kernel⟩, ⟨1820, by decide +kernel⟩),
  (⟨1837, by decide +kernel⟩, ⟨1825, by decide +kernel⟩),
  (⟨1838, by decide +kernel⟩, ⟨1837, by decide +kernel⟩),
  (⟨1839, by decide +kernel⟩, ⟨1819, by decide +kernel⟩),
  (⟨1841, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1841, by decide +kernel⟩, ⟨999, by decide +kernel⟩),
  (⟨1841, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1842, by decide +kernel⟩, ⟨1000, by decide +kernel⟩),
  (⟨1842, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1844, by decide +kernel⟩, ⟨645, by decide +kernel⟩),
  (⟨1844, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1847, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1847, by decide +kernel⟩, ⟨1859, by decide +kernel⟩),
  (⟨1848, by decide +kernel⟩, ⟨1768, by decide +kernel⟩),
  (⟨1848, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1849, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1849, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1851, by decide +kernel⟩, ⟨608, by decide +kernel⟩),
  (⟨1851, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1851, by decide +kernel⟩, ⟨1768, by decide +kernel⟩),
  (⟨1851, by decide +kernel⟩, ⟨1794, by decide +kernel⟩),
  (⟨1851, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1852, by decide +kernel⟩, ⟨641, by decide +kernel⟩),
  (⟨1852, by decide +kernel⟩, ⟨993, by decide +kernel⟩),
  (⟨1852, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨1852, by decide +kernel⟩, ⟨1862, by decide +kernel⟩),
  (⟨1855, by decide +kernel⟩, ⟨1366, by decide +kernel⟩),
  (⟨1855, by decide +kernel⟩, ⟨1766, by decide +kernel⟩),
  (⟨1858, by decide +kernel⟩, ⟨995, by decide +kernel⟩),
  (⟨1859, by decide +kernel⟩, ⟨992, by decide +kernel⟩),
  (⟨1859, by decide +kernel⟩, ⟨1794, by decide +kernel⟩)
]
def edgeBlock69 : List (Fin 1864 × Fin 1864) := [
  (⟨1860, by decide +kernel⟩, ⟨997, by decide +kernel⟩),
  (⟨1863, by decide +kernel⟩, ⟨1860, by decide +kernel⟩),
  (⟨1863, by decide +kernel⟩, ⟨1862, by decide +kernel⟩)
]
def graph : BlockedGraph 1864 := ⟨[edgeBlock0, edgeBlock1, edgeBlock2, edgeBlock3, edgeBlock4, edgeBlock5, edgeBlock6, edgeBlock7, edgeBlock8, edgeBlock9, edgeBlock10, edgeBlock11, edgeBlock12, edgeBlock13, edgeBlock14, edgeBlock15, edgeBlock16, edgeBlock17, edgeBlock18, edgeBlock19, edgeBlock20, edgeBlock21, edgeBlock22, edgeBlock23, edgeBlock24, edgeBlock25, edgeBlock26, edgeBlock27, edgeBlock28, edgeBlock29, edgeBlock30, edgeBlock31, edgeBlock32, edgeBlock33, edgeBlock34, edgeBlock35, edgeBlock36, edgeBlock37, edgeBlock38, edgeBlock39, edgeBlock40, edgeBlock41, edgeBlock42, edgeBlock43, edgeBlock44, edgeBlock45, edgeBlock46, edgeBlock47, edgeBlock48, edgeBlock49, edgeBlock50, edgeBlock51, edgeBlock52, edgeBlock53, edgeBlock54, edgeBlock55, edgeBlock56, edgeBlock57, edgeBlock58, edgeBlock59, edgeBlock60, edgeBlock61, edgeBlock62, edgeBlock63, edgeBlock64, edgeBlock65, edgeBlock66, edgeBlock67, edgeBlock68, edgeBlock69]⟩
def root : Fin 1864 := ⟨995, by decide +kernel⟩
def witnessBlock0 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 32 then
    if v.val < 16 then
      if v.val < 8 then
        if v.val < 4 then
          if v.val < 2 then
            if v.val < 1 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (0, 2)⟩
            else
              none
          else
            if v.val < 3 then
              none
            else
              none
        else
          if v.val < 6 then
            if v.val < 5 then
              none
            else
              some ⟨⟨1753, by decide +kernel⟩, 2, some (0, 9)⟩
          else
            if v.val < 7 then
              none
            else
              none
      else
        if v.val < 12 then
          if v.val < 10 then
            if v.val < 9 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (0, 12)⟩
            else
              none
          else
            if v.val < 11 then
              none
            else
              none
        else
          if v.val < 14 then
            if v.val < 13 then
              none
            else
              none
          else
            if v.val < 15 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (0, 21)⟩
    else
      if v.val < 24 then
        if v.val < 20 then
          if v.val < 18 then
            if v.val < 17 then
              none
            else
              none
          else
            if v.val < 19 then
              none
            else
              none
        else
          if v.val < 22 then
            if v.val < 21 then
              none
            else
              none
          else
            if v.val < 23 then
              some ⟨⟨5, by decide +kernel⟩, 3, some (0, 39)⟩
            else
              none
      else
        if v.val < 28 then
          if v.val < 26 then
            if v.val < 25 then
              none
            else
              none
          else
            if v.val < 27 then
              some ⟨⟨8, by decide +kernel⟩, 2, some (0, 45)⟩
            else
              none
        else
          if v.val < 30 then
            if v.val < 29 then
              none
            else
              none
          else
            if v.val < 31 then
              none
            else
              none
  else
    if v.val < 48 then
      if v.val < 40 then
        if v.val < 36 then
          if v.val < 34 then
            if v.val < 33 then
              none
            else
              none
          else
            if v.val < 35 then
              none
            else
              none
        else
          if v.val < 38 then
            if v.val < 37 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (0, 51)⟩
          else
            if v.val < 39 then
              none
            else
              none
      else
        if v.val < 44 then
          if v.val < 42 then
            if v.val < 41 then
              none
            else
              none
          else
            if v.val < 43 then
              none
            else
              none
        else
          if v.val < 46 then
            if v.val < 45 then
              some ⟨⟨357, by decide +kernel⟩, 3, some (0, 59)⟩
            else
              none
          else
            if v.val < 47 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (1, 7)⟩
            else
              none
    else
      if v.val < 56 then
        if v.val < 52 then
          if v.val < 50 then
            if v.val < 49 then
              none
            else
              none
          else
            if v.val < 51 then
              some ⟨⟨526, by decide +kernel⟩, 2, some (1, 15)⟩
            else
              none
        else
          if v.val < 54 then
            if v.val < 53 then
              none
            else
              none
          else
            if v.val < 55 then
              none
            else
              none
      else
        if v.val < 60 then
          if v.val < 58 then
            if v.val < 57 then
              none
            else
              none
          else
            if v.val < 59 then
              none
            else
              none
        else
          if v.val < 62 then
            if v.val < 61 then
              some ⟨⟨5, by decide +kernel⟩, 3, some (1, 29)⟩
            else
              some ⟨⟨1753, by decide +kernel⟩, 2, some (1, 35)⟩
          else
            if v.val < 63 then
              none
            else
              none
def witnessBlock1 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 96 then
    if v.val < 80 then
      if v.val < 72 then
        if v.val < 68 then
          if v.val < 66 then
            if v.val < 65 then
              none
            else
              none
          else
            if v.val < 67 then
              none
            else
              none
        else
          if v.val < 70 then
            if v.val < 69 then
              none
            else
              none
          else
            if v.val < 71 then
              none
            else
              none
      else
        if v.val < 76 then
          if v.val < 74 then
            if v.val < 73 then
              none
            else
              none
          else
            if v.val < 75 then
              none
            else
              none
        else
          if v.val < 78 then
            if v.val < 77 then
              none
            else
              none
          else
            if v.val < 79 then
              none
            else
              none
    else
      if v.val < 88 then
        if v.val < 84 then
          if v.val < 82 then
            if v.val < 81 then
              none
            else
              none
          else
            if v.val < 83 then
              none
            else
              none
        else
          if v.val < 86 then
            if v.val < 85 then
              none
            else
              none
          else
            if v.val < 87 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (1, 52)⟩
            else
              none
      else
        if v.val < 92 then
          if v.val < 90 then
            if v.val < 89 then
              some ⟨⟨645, by decide +kernel⟩, 2, some (1, 54)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (1, 60)⟩
          else
            if v.val < 91 then
              some ⟨⟨567, by decide +kernel⟩, 2, some (2, 0)⟩
            else
              none
        else
          if v.val < 94 then
            if v.val < 93 then
              none
            else
              none
          else
            if v.val < 95 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (2, 16)⟩
            else
              none
  else
    if v.val < 112 then
      if v.val < 104 then
        if v.val < 100 then
          if v.val < 98 then
            if v.val < 97 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (2, 26)⟩
            else
              none
          else
            if v.val < 99 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (2, 30)⟩
            else
              none
        else
          if v.val < 102 then
            if v.val < 101 then
              none
            else
              none
          else
            if v.val < 103 then
              none
            else
              none
      else
        if v.val < 108 then
          if v.val < 106 then
            if v.val < 105 then
              none
            else
              none
          else
            if v.val < 107 then
              none
            else
              none
        else
          if v.val < 110 then
            if v.val < 109 then
              none
            else
              none
          else
            if v.val < 111 then
              none
            else
              none
    else
      if v.val < 120 then
        if v.val < 116 then
          if v.val < 114 then
            if v.val < 113 then
              none
            else
              none
          else
            if v.val < 115 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (2, 61)⟩
            else
              some ⟨⟨114, by decide +kernel⟩, 2, some (2, 63)⟩
        else
          if v.val < 118 then
            if v.val < 117 then
              some ⟨⟨114, by decide +kernel⟩, 2, some (3, 0)⟩
            else
              some ⟨⟨118, by decide +kernel⟩, 2, some (3, 1)⟩
          else
            if v.val < 119 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (3, 3)⟩
            else
              none
      else
        if v.val < 124 then
          if v.val < 122 then
            if v.val < 121 then
              none
            else
              none
          else
            if v.val < 123 then
              none
            else
              none
        else
          if v.val < 126 then
            if v.val < 125 then
              none
            else
              none
          else
            if v.val < 127 then
              none
            else
              none
def witnessBlock2 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 160 then
    if v.val < 144 then
      if v.val < 136 then
        if v.val < 132 then
          if v.val < 130 then
            if v.val < 129 then
              none
            else
              none
          else
            if v.val < 131 then
              none
            else
              none
        else
          if v.val < 134 then
            if v.val < 133 then
              none
            else
              none
          else
            if v.val < 135 then
              none
            else
              none
      else
        if v.val < 140 then
          if v.val < 138 then
            if v.val < 137 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (3, 27)⟩
            else
              none
          else
            if v.val < 139 then
              none
            else
              none
        else
          if v.val < 142 then
            if v.val < 141 then
              none
            else
              none
          else
            if v.val < 143 then
              none
            else
              none
    else
      if v.val < 152 then
        if v.val < 148 then
          if v.val < 146 then
            if v.val < 145 then
              none
            else
              none
          else
            if v.val < 147 then
              none
            else
              none
        else
          if v.val < 150 then
            if v.val < 149 then
              none
            else
              none
          else
            if v.val < 151 then
              none
            else
              none
      else
        if v.val < 156 then
          if v.val < 154 then
            if v.val < 153 then
              none
            else
              none
          else
            if v.val < 155 then
              some ⟨⟨8, by decide +kernel⟩, 2, some (3, 42)⟩
            else
              none
        else
          if v.val < 158 then
            if v.val < 157 then
              none
            else
              none
          else
            if v.val < 159 then
              none
            else
              none
  else
    if v.val < 176 then
      if v.val < 168 then
        if v.val < 164 then
          if v.val < 162 then
            if v.val < 161 then
              none
            else
              none
          else
            if v.val < 163 then
              none
            else
              none
        else
          if v.val < 166 then
            if v.val < 165 then
              none
            else
              none
          else
            if v.val < 167 then
              some ⟨⟨584, by decide +kernel⟩, 2, some (3, 52)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (3, 54)⟩
      else
        if v.val < 172 then
          if v.val < 170 then
            if v.val < 169 then
              none
            else
              none
          else
            if v.val < 171 then
              some ⟨⟨590, by decide +kernel⟩, 2, some (3, 59)⟩
            else
              none
        else
          if v.val < 174 then
            if v.val < 173 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (4, 1)⟩
          else
            if v.val < 175 then
              none
            else
              none
    else
      if v.val < 184 then
        if v.val < 180 then
          if v.val < 178 then
            if v.val < 177 then
              none
            else
              none
          else
            if v.val < 179 then
              none
            else
              none
        else
          if v.val < 182 then
            if v.val < 181 then
              none
            else
              none
          else
            if v.val < 183 then
              none
            else
              none
      else
        if v.val < 188 then
          if v.val < 186 then
            if v.val < 185 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (4, 9)⟩
          else
            if v.val < 187 then
              none
            else
              none
        else
          if v.val < 190 then
            if v.val < 189 then
              none
            else
              none
          else
            if v.val < 191 then
              none
            else
              none
def witnessBlock3 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 224 then
    if v.val < 208 then
      if v.val < 200 then
        if v.val < 196 then
          if v.val < 194 then
            if v.val < 193 then
              none
            else
              none
          else
            if v.val < 195 then
              none
            else
              some ⟨⟨1050, by decide +kernel⟩, 2, some (4, 18)⟩
        else
          if v.val < 198 then
            if v.val < 197 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (4, 19)⟩
            else
              none
          else
            if v.val < 199 then
              none
            else
              none
      else
        if v.val < 204 then
          if v.val < 202 then
            if v.val < 201 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (4, 28)⟩
            else
              none
          else
            if v.val < 203 then
              none
            else
              none
        else
          if v.val < 206 then
            if v.val < 205 then
              none
            else
              none
          else
            if v.val < 207 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (4, 38)⟩
    else
      if v.val < 216 then
        if v.val < 212 then
          if v.val < 210 then
            if v.val < 209 then
              none
            else
              some ⟨⟨645, by decide +kernel⟩, 2, some (4, 39)⟩
          else
            if v.val < 211 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (4, 44)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (4, 45)⟩
        else
          if v.val < 214 then
            if v.val < 213 then
              none
            else
              some ⟨⟨645, by decide +kernel⟩, 2, some (4, 47)⟩
          else
            if v.val < 215 then
              some ⟨⟨645, by decide +kernel⟩, 2, some (4, 50)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (4, 56)⟩
      else
        if v.val < 220 then
          if v.val < 218 then
            if v.val < 217 then
              none
            else
              none
          else
            if v.val < 219 then
              none
            else
              none
        else
          if v.val < 222 then
            if v.val < 221 then
              none
            else
              none
          else
            if v.val < 223 then
              none
            else
              none
  else
    if v.val < 240 then
      if v.val < 232 then
        if v.val < 228 then
          if v.val < 226 then
            if v.val < 225 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (5, 2)⟩
            else
              none
          else
            if v.val < 227 then
              none
            else
              none
        else
          if v.val < 230 then
            if v.val < 229 then
              none
            else
              none
          else
            if v.val < 231 then
              none
            else
              none
      else
        if v.val < 236 then
          if v.val < 234 then
            if v.val < 233 then
              none
            else
              none
          else
            if v.val < 235 then
              none
            else
              none
        else
          if v.val < 238 then
            if v.val < 237 then
              none
            else
              some ⟨⟨718, by decide +kernel⟩, 2, some (5, 19)⟩
          else
            if v.val < 239 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (5, 22)⟩
    else
      if v.val < 248 then
        if v.val < 244 then
          if v.val < 242 then
            if v.val < 241 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (5, 28)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (5, 34)⟩
          else
            if v.val < 243 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (5, 37)⟩
        else
          if v.val < 246 then
            if v.val < 245 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (5, 42)⟩
            else
              none
          else
            if v.val < 247 then
              none
            else
              none
      else
        if v.val < 252 then
          if v.val < 250 then
            if v.val < 249 then
              none
            else
              none
          else
            if v.val < 251 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (5, 47)⟩
            else
              none
        else
          if v.val < 254 then
            if v.val < 253 then
              none
            else
              none
          else
            if v.val < 255 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (5, 56)⟩
def witnessBlock4 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 288 then
    if v.val < 272 then
      if v.val < 264 then
        if v.val < 260 then
          if v.val < 258 then
            if v.val < 257 then
              none
            else
              some ⟨⟨255, by decide +kernel⟩, 2, some (6, 3)⟩
          else
            if v.val < 259 then
              none
            else
              none
        else
          if v.val < 262 then
            if v.val < 261 then
              none
            else
              none
          else
            if v.val < 263 then
              none
            else
              some ⟨⟨732, by decide +kernel⟩, 2, some (6, 15)⟩
      else
        if v.val < 268 then
          if v.val < 266 then
            if v.val < 265 then
              none
            else
              some ⟨⟨677, by decide +kernel⟩, 3, some (6, 25)⟩
          else
            if v.val < 267 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (6, 30)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (6, 31)⟩
        else
          if v.val < 270 then
            if v.val < 269 then
              none
            else
              none
          else
            if v.val < 271 then
              none
            else
              none
    else
      if v.val < 280 then
        if v.val < 276 then
          if v.val < 274 then
            if v.val < 273 then
              none
            else
              none
          else
            if v.val < 275 then
              none
            else
              none
        else
          if v.val < 278 then
            if v.val < 277 then
              none
            else
              none
          else
            if v.val < 279 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (6, 56)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (6, 61)⟩
      else
        if v.val < 284 then
          if v.val < 282 then
            if v.val < 281 then
              none
            else
              none
          else
            if v.val < 283 then
              none
            else
              none
        else
          if v.val < 286 then
            if v.val < 285 then
              none
            else
              none
          else
            if v.val < 287 then
              none
            else
              none
  else
    if v.val < 304 then
      if v.val < 296 then
        if v.val < 292 then
          if v.val < 290 then
            if v.val < 289 then
              none
            else
              none
          else
            if v.val < 291 then
              none
            else
              none
        else
          if v.val < 294 then
            if v.val < 293 then
              none
            else
              none
          else
            if v.val < 295 then
              none
            else
              none
      else
        if v.val < 300 then
          if v.val < 298 then
            if v.val < 297 then
              none
            else
              none
          else
            if v.val < 299 then
              none
            else
              none
        else
          if v.val < 302 then
            if v.val < 301 then
              none
            else
              none
          else
            if v.val < 303 then
              none
            else
              none
    else
      if v.val < 312 then
        if v.val < 308 then
          if v.val < 306 then
            if v.val < 305 then
              none
            else
              none
          else
            if v.val < 307 then
              none
            else
              none
        else
          if v.val < 310 then
            if v.val < 309 then
              none
            else
              none
          else
            if v.val < 311 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (7, 61)⟩
      else
        if v.val < 316 then
          if v.val < 314 then
            if v.val < 313 then
              none
            else
              none
          else
            if v.val < 315 then
              none
            else
              none
        else
          if v.val < 318 then
            if v.val < 317 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (8, 10)⟩
          else
            if v.val < 319 then
              none
            else
              none
def witnessBlock5 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 352 then
    if v.val < 336 then
      if v.val < 328 then
        if v.val < 324 then
          if v.val < 322 then
            if v.val < 321 then
              none
            else
              none
          else
            if v.val < 323 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (8, 24)⟩
        else
          if v.val < 326 then
            if v.val < 325 then
              none
            else
              none
          else
            if v.val < 327 then
              none
            else
              none
      else
        if v.val < 332 then
          if v.val < 330 then
            if v.val < 329 then
              none
            else
              none
          else
            if v.val < 331 then
              none
            else
              none
        else
          if v.val < 334 then
            if v.val < 333 then
              none
            else
              none
          else
            if v.val < 335 then
              none
            else
              none
    else
      if v.val < 344 then
        if v.val < 340 then
          if v.val < 338 then
            if v.val < 337 then
              none
            else
              none
          else
            if v.val < 339 then
              none
            else
              none
        else
          if v.val < 342 then
            if v.val < 341 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (8, 37)⟩
          else
            if v.val < 343 then
              none
            else
              none
      else
        if v.val < 348 then
          if v.val < 346 then
            if v.val < 345 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (8, 41)⟩
            else
              none
          else
            if v.val < 347 then
              none
            else
              none
        else
          if v.val < 350 then
            if v.val < 349 then
              none
            else
              none
          else
            if v.val < 351 then
              none
            else
              none
  else
    if v.val < 368 then
      if v.val < 360 then
        if v.val < 356 then
          if v.val < 354 then
            if v.val < 353 then
              none
            else
              none
          else
            if v.val < 355 then
              none
            else
              none
        else
          if v.val < 358 then
            if v.val < 357 then
              none
            else
              some ⟨⟨528, by decide +kernel⟩, 2, some (8, 53)⟩
          else
            if v.val < 359 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (8, 55)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (8, 56)⟩
      else
        if v.val < 364 then
          if v.val < 362 then
            if v.val < 361 then
              none
            else
              none
          else
            if v.val < 363 then
              none
            else
              none
        else
          if v.val < 366 then
            if v.val < 365 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (8, 62)⟩
            else
              none
          else
            if v.val < 367 then
              none
            else
              none
    else
      if v.val < 376 then
        if v.val < 372 then
          if v.val < 370 then
            if v.val < 369 then
              none
            else
              none
          else
            if v.val < 371 then
              some ⟨⟨382, by decide +kernel⟩, 2, some (9, 17)⟩
            else
              none
        else
          if v.val < 374 then
            if v.val < 373 then
              none
            else
              none
          else
            if v.val < 375 then
              none
            else
              none
      else
        if v.val < 380 then
          if v.val < 378 then
            if v.val < 377 then
              none
            else
              none
          else
            if v.val < 379 then
              none
            else
              none
        else
          if v.val < 382 then
            if v.val < 381 then
              none
            else
              none
          else
            if v.val < 383 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (9, 63)⟩
            else
              none
def witnessBlock6 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 416 then
    if v.val < 400 then
      if v.val < 392 then
        if v.val < 388 then
          if v.val < 386 then
            if v.val < 385 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (10, 1)⟩
            else
              none
          else
            if v.val < 387 then
              none
            else
              none
        else
          if v.val < 390 then
            if v.val < 389 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (10, 8)⟩
            else
              none
          else
            if v.val < 391 then
              none
            else
              none
      else
        if v.val < 396 then
          if v.val < 394 then
            if v.val < 393 then
              none
            else
              none
          else
            if v.val < 395 then
              none
            else
              none
        else
          if v.val < 398 then
            if v.val < 397 then
              none
            else
              none
          else
            if v.val < 399 then
              some ⟨⟨1081, by decide +kernel⟩, 3, some (10, 23)⟩
            else
              none
    else
      if v.val < 408 then
        if v.val < 404 then
          if v.val < 402 then
            if v.val < 401 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (10, 25)⟩
            else
              none
          else
            if v.val < 403 then
              none
            else
              none
        else
          if v.val < 406 then
            if v.val < 405 then
              none
            else
              none
          else
            if v.val < 407 then
              none
            else
              none
      else
        if v.val < 412 then
          if v.val < 410 then
            if v.val < 409 then
              none
            else
              none
          else
            if v.val < 411 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (10, 35)⟩
            else
              none
        else
          if v.val < 414 then
            if v.val < 413 then
              none
            else
              none
          else
            if v.val < 415 then
              none
            else
              some ⟨⟨1241, by decide +kernel⟩, 2, some (10, 40)⟩
  else
    if v.val < 432 then
      if v.val < 424 then
        if v.val < 420 then
          if v.val < 418 then
            if v.val < 417 then
              none
            else
              none
          else
            if v.val < 419 then
              none
            else
              none
        else
          if v.val < 422 then
            if v.val < 421 then
              none
            else
              none
          else
            if v.val < 423 then
              none
            else
              none
      else
        if v.val < 428 then
          if v.val < 426 then
            if v.val < 425 then
              none
            else
              none
          else
            if v.val < 427 then
              none
            else
              none
        else
          if v.val < 430 then
            if v.val < 429 then
              none
            else
              none
          else
            if v.val < 431 then
              none
            else
              none
    else
      if v.val < 440 then
        if v.val < 436 then
          if v.val < 434 then
            if v.val < 433 then
              none
            else
              none
          else
            if v.val < 435 then
              none
            else
              none
        else
          if v.val < 438 then
            if v.val < 437 then
              none
            else
              none
          else
            if v.val < 439 then
              none
            else
              none
      else
        if v.val < 444 then
          if v.val < 442 then
            if v.val < 441 then
              none
            else
              some ⟨⟨524, by decide +kernel⟩, 3, some (11, 11)⟩
          else
            if v.val < 443 then
              none
            else
              some ⟨⟨446, by decide +kernel⟩, 2, some (11, 16)⟩
        else
          if v.val < 446 then
            if v.val < 445 then
              none
            else
              none
          else
            if v.val < 447 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (11, 26)⟩
            else
              none
def witnessBlock7 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 480 then
    if v.val < 464 then
      if v.val < 456 then
        if v.val < 452 then
          if v.val < 450 then
            if v.val < 449 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (11, 30)⟩
          else
            if v.val < 451 then
              none
            else
              none
        else
          if v.val < 454 then
            if v.val < 453 then
              none
            else
              none
          else
            if v.val < 455 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (11, 35)⟩
            else
              none
      else
        if v.val < 460 then
          if v.val < 458 then
            if v.val < 457 then
              none
            else
              none
          else
            if v.val < 459 then
              none
            else
              none
        else
          if v.val < 462 then
            if v.val < 461 then
              none
            else
              none
          else
            if v.val < 463 then
              none
            else
              none
    else
      if v.val < 472 then
        if v.val < 468 then
          if v.val < 466 then
            if v.val < 465 then
              none
            else
              none
          else
            if v.val < 467 then
              none
            else
              none
        else
          if v.val < 470 then
            if v.val < 469 then
              some ⟨⟨359, by decide +kernel⟩, 2, some (11, 54)⟩
            else
              none
          else
            if v.val < 471 then
              none
            else
              some ⟨⟨472, by decide +kernel⟩, 2, some (11, 57)⟩
      else
        if v.val < 476 then
          if v.val < 474 then
            if v.val < 473 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (11, 61)⟩
            else
              some ⟨⟨474, by decide +kernel⟩, 2, some (11, 62)⟩
          else
            if v.val < 475 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (12, 0)⟩
            else
              none
        else
          if v.val < 478 then
            if v.val < 477 then
              none
            else
              none
          else
            if v.val < 479 then
              none
            else
              some ⟨⟨472, by decide +kernel⟩, 2, some (12, 7)⟩
  else
    if v.val < 496 then
      if v.val < 488 then
        if v.val < 484 then
          if v.val < 482 then
            if v.val < 481 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (12, 17)⟩
          else
            if v.val < 483 then
              some ⟨⟨1170, by decide +kernel⟩, 2, some (12, 25)⟩
            else
              none
        else
          if v.val < 486 then
            if v.val < 485 then
              none
            else
              none
          else
            if v.val < 487 then
              none
            else
              some ⟨⟨1281, by decide +kernel⟩, 2, some (12, 37)⟩
      else
        if v.val < 492 then
          if v.val < 490 then
            if v.val < 489 then
              none
            else
              none
          else
            if v.val < 491 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (12, 46)⟩
            else
              none
        else
          if v.val < 494 then
            if v.val < 493 then
              none
            else
              none
          else
            if v.val < 495 then
              none
            else
              none
    else
      if v.val < 504 then
        if v.val < 500 then
          if v.val < 498 then
            if v.val < 497 then
              none
            else
              none
          else
            if v.val < 499 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (12, 58)⟩
            else
              none
        else
          if v.val < 502 then
            if v.val < 501 then
              none
            else
              none
          else
            if v.val < 503 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (13, 3)⟩
            else
              none
      else
        if v.val < 508 then
          if v.val < 506 then
            if v.val < 505 then
              none
            else
              none
          else
            if v.val < 507 then
              none
            else
              none
        else
          if v.val < 510 then
            if v.val < 509 then
              none
            else
              none
          else
            if v.val < 511 then
              none
            else
              none
def witnessBlock8 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 544 then
    if v.val < 528 then
      if v.val < 520 then
        if v.val < 516 then
          if v.val < 514 then
            if v.val < 513 then
              none
            else
              none
          else
            if v.val < 515 then
              none
            else
              none
        else
          if v.val < 518 then
            if v.val < 517 then
              none
            else
              none
          else
            if v.val < 519 then
              none
            else
              none
      else
        if v.val < 524 then
          if v.val < 522 then
            if v.val < 521 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (13, 15)⟩
          else
            if v.val < 523 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (13, 16)⟩
            else
              none
        else
          if v.val < 526 then
            if v.val < 525 then
              some ⟨⟨521, by decide +kernel⟩, 2, some (13, 21)⟩
            else
              none
          else
            if v.val < 527 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (13, 30)⟩
            else
              none
    else
      if v.val < 536 then
        if v.val < 532 then
          if v.val < 530 then
            if v.val < 529 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (13, 31)⟩
            else
              none
          else
            if v.val < 531 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (13, 32)⟩
            else
              none
        else
          if v.val < 534 then
            if v.val < 533 then
              some ⟨⟨1273, by decide +kernel⟩, 4, some (13, 35)⟩
            else
              none
          else
            if v.val < 535 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (13, 37)⟩
            else
              none
      else
        if v.val < 540 then
          if v.val < 538 then
            if v.val < 537 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (13, 40)⟩
            else
              none
          else
            if v.val < 539 then
              none
            else
              some ⟨⟨905, by decide +kernel⟩, 4, some (13, 44)⟩
        else
          if v.val < 542 then
            if v.val < 541 then
              none
            else
              none
          else
            if v.val < 543 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (13, 47)⟩
  else
    if v.val < 560 then
      if v.val < 552 then
        if v.val < 548 then
          if v.val < 546 then
            if v.val < 545 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (13, 48)⟩
            else
              some ⟨⟨550, by decide +kernel⟩, 2, some (13, 49)⟩
          else
            if v.val < 547 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (13, 54)⟩
            else
              none
        else
          if v.val < 550 then
            if v.val < 549 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (13, 57)⟩
          else
            if v.val < 551 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (13, 61)⟩
            else
              some ⟨⟨550, by decide +kernel⟩, 2, some (14, 1)⟩
      else
        if v.val < 556 then
          if v.val < 554 then
            if v.val < 553 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (14, 9)⟩
          else
            if v.val < 555 then
              none
            else
              none
        else
          if v.val < 558 then
            if v.val < 557 then
              some ⟨⟨557, by decide +kernel⟩, 2, some (14, 15)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (14, 24)⟩
          else
            if v.val < 559 then
              some ⟨⟨557, by decide +kernel⟩, 2, some (14, 26)⟩
            else
              none
    else
      if v.val < 568 then
        if v.val < 564 then
          if v.val < 562 then
            if v.val < 561 then
              some ⟨⟨557, by decide +kernel⟩, 2, some (14, 28)⟩
            else
              none
          else
            if v.val < 563 then
              none
            else
              some ⟨⟨567, by decide +kernel⟩, 2, some (14, 44)⟩
        else
          if v.val < 566 then
            if v.val < 565 then
              none
            else
              none
          else
            if v.val < 567 then
              some ⟨⟨567, by decide +kernel⟩, 2, some (14, 52)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (15, 4)⟩
      else
        if v.val < 572 then
          if v.val < 570 then
            if v.val < 569 then
              some ⟨⟨930, by decide +kernel⟩, 2, some (15, 9)⟩
            else
              some ⟨⟨937, by decide +kernel⟩, 2, some (15, 10)⟩
          else
            if v.val < 571 then
              some ⟨⟨930, by decide +kernel⟩, 2, some (15, 11)⟩
            else
              some ⟨⟨930, by decide +kernel⟩, 2, some (15, 13)⟩
        else
          if v.val < 574 then
            if v.val < 573 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (15, 16)⟩
            else
              none
          else
            if v.val < 575 then
              none
            else
              none
def witnessBlock9 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 608 then
    if v.val < 592 then
      if v.val < 584 then
        if v.val < 580 then
          if v.val < 578 then
            if v.val < 577 then
              none
            else
              none
          else
            if v.val < 579 then
              none
            else
              none
        else
          if v.val < 582 then
            if v.val < 581 then
              none
            else
              none
          else
            if v.val < 583 then
              some ⟨⟨584, by decide +kernel⟩, 2, some (15, 31)⟩
            else
              some ⟨⟨584, by decide +kernel⟩, 2, some (15, 32)⟩
      else
        if v.val < 588 then
          if v.val < 586 then
            if v.val < 585 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (15, 38)⟩
            else
              none
          else
            if v.val < 587 then
              none
            else
              none
        else
          if v.val < 590 then
            if v.val < 589 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (15, 44)⟩
            else
              none
          else
            if v.val < 591 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (15, 45)⟩
            else
              none
    else
      if v.val < 600 then
        if v.val < 596 then
          if v.val < 594 then
            if v.val < 593 then
              none
            else
              none
          else
            if v.val < 595 then
              none
            else
              none
        else
          if v.val < 598 then
            if v.val < 597 then
              none
            else
              none
          else
            if v.val < 599 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (15, 55)⟩
            else
              none
      else
        if v.val < 604 then
          if v.val < 602 then
            if v.val < 601 then
              none
            else
              some ⟨⟨1084, by decide +kernel⟩, 2, some (15, 59)⟩
          else
            if v.val < 603 then
              none
            else
              none
        else
          if v.val < 606 then
            if v.val < 605 then
              none
            else
              none
          else
            if v.val < 607 then
              some ⟨⟨626, by decide +kernel⟩, 2, some (16, 5)⟩
            else
              none
  else
    if v.val < 624 then
      if v.val < 616 then
        if v.val < 612 then
          if v.val < 610 then
            if v.val < 609 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (16, 6)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (16, 8)⟩
          else
            if v.val < 611 then
              none
            else
              none
        else
          if v.val < 614 then
            if v.val < 613 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (16, 24)⟩
          else
            if v.val < 615 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (16, 29)⟩
      else
        if v.val < 620 then
          if v.val < 618 then
            if v.val < 617 then
              none
            else
              none
          else
            if v.val < 619 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (16, 34)⟩
            else
              none
        else
          if v.val < 622 then
            if v.val < 621 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (16, 41)⟩
            else
              some ⟨⟨620, by decide +kernel⟩, 2, some (16, 48)⟩
          else
            if v.val < 623 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (16, 49)⟩
            else
              none
    else
      if v.val < 632 then
        if v.val < 628 then
          if v.val < 626 then
            if v.val < 625 then
              none
            else
              none
          else
            if v.val < 627 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (16, 54)⟩
            else
              some ⟨⟨626, by decide +kernel⟩, 2, some (16, 55)⟩
        else
          if v.val < 630 then
            if v.val < 629 then
              none
            else
              none
          else
            if v.val < 631 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (16, 58)⟩
      else
        if v.val < 636 then
          if v.val < 634 then
            if v.val < 633 then
              none
            else
              some ⟨⟨636, by decide +kernel⟩, 2, some (16, 62)⟩
          else
            if v.val < 635 then
              some ⟨⟨1342, by decide +kernel⟩, 3, some (17, 11)⟩
            else
              none
        else
          if v.val < 638 then
            if v.val < 637 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (17, 12)⟩
            else
              none
          else
            if v.val < 639 then
              none
            else
              none
def witnessBlock10 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 672 then
    if v.val < 656 then
      if v.val < 648 then
        if v.val < 644 then
          if v.val < 642 then
            if v.val < 641 then
              none
            else
              none
          else
            if v.val < 643 then
              none
            else
              none
        else
          if v.val < 646 then
            if v.val < 645 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (17, 23)⟩
          else
            if v.val < 647 then
              none
            else
              none
      else
        if v.val < 652 then
          if v.val < 650 then
            if v.val < 649 then
              none
            else
              none
          else
            if v.val < 651 then
              none
            else
              none
        else
          if v.val < 654 then
            if v.val < 653 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (17, 40)⟩
          else
            if v.val < 655 then
              some ⟨⟨1233, by decide +kernel⟩, 2, some (17, 43)⟩
            else
              some ⟨⟨1233, by decide +kernel⟩, 2, some (17, 47)⟩
    else
      if v.val < 664 then
        if v.val < 660 then
          if v.val < 658 then
            if v.val < 657 then
              none
            else
              none
          else
            if v.val < 659 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (17, 50)⟩
        else
          if v.val < 662 then
            if v.val < 661 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (17, 54)⟩
          else
            if v.val < 663 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (18, 0)⟩
            else
              none
      else
        if v.val < 668 then
          if v.val < 666 then
            if v.val < 665 then
              none
            else
              none
          else
            if v.val < 667 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (18, 13)⟩
            else
              none
        else
          if v.val < 670 then
            if v.val < 669 then
              none
            else
              none
          else
            if v.val < 671 then
              none
            else
              none
  else
    if v.val < 688 then
      if v.val < 680 then
        if v.val < 676 then
          if v.val < 674 then
            if v.val < 673 then
              none
            else
              none
          else
            if v.val < 675 then
              none
            else
              none
        else
          if v.val < 678 then
            if v.val < 677 then
              none
            else
              some ⟨⟨726, by decide +kernel⟩, 2, some (18, 32)⟩
          else
            if v.val < 679 then
              none
            else
              none
      else
        if v.val < 684 then
          if v.val < 682 then
            if v.val < 681 then
              none
            else
              some ⟨⟨1753, by decide +kernel⟩, 2, some (18, 53)⟩
          else
            if v.val < 683 then
              none
            else
              none
        else
          if v.val < 686 then
            if v.val < 685 then
              none
            else
              none
          else
            if v.val < 687 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (19, 10)⟩
            else
              none
    else
      if v.val < 696 then
        if v.val < 692 then
          if v.val < 690 then
            if v.val < 689 then
              none
            else
              none
          else
            if v.val < 691 then
              none
            else
              none
        else
          if v.val < 694 then
            if v.val < 693 then
              none
            else
              none
          else
            if v.val < 695 then
              none
            else
              none
      else
        if v.val < 700 then
          if v.val < 698 then
            if v.val < 697 then
              none
            else
              none
          else
            if v.val < 699 then
              some ⟨⟨700, by decide +kernel⟩, 2, some (19, 44)⟩
            else
              none
        else
          if v.val < 702 then
            if v.val < 701 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (19, 61)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (20, 2)⟩
          else
            if v.val < 703 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (20, 4)⟩
def witnessBlock11 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 736 then
    if v.val < 720 then
      if v.val < 712 then
        if v.val < 708 then
          if v.val < 706 then
            if v.val < 705 then
              none
            else
              some ⟨⟨715, by decide +kernel⟩, 2, some (20, 11)⟩
          else
            if v.val < 707 then
              none
            else
              some ⟨⟨973, by decide +kernel⟩, 2, some (20, 22)⟩
        else
          if v.val < 710 then
            if v.val < 709 then
              some ⟨⟨715, by decide +kernel⟩, 2, some (20, 25)⟩
            else
              none
          else
            if v.val < 711 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (20, 32)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (20, 49)⟩
      else
        if v.val < 716 then
          if v.val < 714 then
            if v.val < 713 then
              none
            else
              none
          else
            if v.val < 715 then
              some ⟨⟨708, by decide +kernel⟩, 3, some (20, 60)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (21, 0)⟩
        else
          if v.val < 718 then
            if v.val < 717 then
              some ⟨⟨707, by decide +kernel⟩, 3, some (21, 2)⟩
            else
              none
          else
            if v.val < 719 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (21, 7)⟩
            else
              none
    else
      if v.val < 728 then
        if v.val < 724 then
          if v.val < 722 then
            if v.val < 721 then
              none
            else
              none
          else
            if v.val < 723 then
              none
            else
              some ⟨⟨724, by decide +kernel⟩, 2, some (21, 14)⟩
        else
          if v.val < 726 then
            if v.val < 725 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (21, 18)⟩
            else
              none
          else
            if v.val < 727 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (21, 25)⟩
            else
              none
      else
        if v.val < 732 then
          if v.val < 730 then
            if v.val < 729 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (21, 29)⟩
          else
            if v.val < 731 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (21, 31)⟩
            else
              none
        else
          if v.val < 734 then
            if v.val < 733 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (21, 35)⟩
            else
              none
          else
            if v.val < 735 then
              none
            else
              none
  else
    if v.val < 752 then
      if v.val < 744 then
        if v.val < 740 then
          if v.val < 738 then
            if v.val < 737 then
              none
            else
              none
          else
            if v.val < 739 then
              none
            else
              none
        else
          if v.val < 742 then
            if v.val < 741 then
              none
            else
              none
          else
            if v.val < 743 then
              none
            else
              none
      else
        if v.val < 748 then
          if v.val < 746 then
            if v.val < 745 then
              some ⟨⟨700, by decide +kernel⟩, 2, some (21, 50)⟩
            else
              none
          else
            if v.val < 747 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (21, 55)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (21, 60)⟩
        else
          if v.val < 750 then
            if v.val < 749 then
              some ⟨⟨754, by decide +kernel⟩, 2, some (21, 62)⟩
            else
              none
          else
            if v.val < 751 then
              none
            else
              none
    else
      if v.val < 760 then
        if v.val < 756 then
          if v.val < 754 then
            if v.val < 753 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (22, 14)⟩
            else
              none
          else
            if v.val < 755 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (22, 23)⟩
            else
              none
        else
          if v.val < 758 then
            if v.val < 757 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (23, 12)⟩
          else
            if v.val < 759 then
              some ⟨⟨930, by decide +kernel⟩, 2, some (23, 15)⟩
            else
              none
      else
        if v.val < 764 then
          if v.val < 762 then
            if v.val < 761 then
              none
            else
              none
          else
            if v.val < 763 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (23, 23)⟩
            else
              none
        else
          if v.val < 766 then
            if v.val < 765 then
              some ⟨⟨1520, by decide +kernel⟩, 2, some (23, 55)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (24, 7)⟩
          else
            if v.val < 767 then
              none
            else
              none
def witnessBlock12 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 800 then
    if v.val < 784 then
      if v.val < 776 then
        if v.val < 772 then
          if v.val < 770 then
            if v.val < 769 then
              none
            else
              none
          else
            if v.val < 771 then
              none
            else
              some ⟨⟨1788, by decide +kernel⟩, 2, some (24, 22)⟩
        else
          if v.val < 774 then
            if v.val < 773 then
              none
            else
              none
          else
            if v.val < 775 then
              none
            else
              none
      else
        if v.val < 780 then
          if v.val < 778 then
            if v.val < 777 then
              none
            else
              none
          else
            if v.val < 779 then
              none
            else
              none
        else
          if v.val < 782 then
            if v.val < 781 then
              none
            else
              none
          else
            if v.val < 783 then
              none
            else
              some ⟨⟨930, by decide +kernel⟩, 2, some (24, 32)⟩
    else
      if v.val < 792 then
        if v.val < 788 then
          if v.val < 786 then
            if v.val < 785 then
              none
            else
              none
          else
            if v.val < 787 then
              none
            else
              none
        else
          if v.val < 790 then
            if v.val < 789 then
              none
            else
              none
          else
            if v.val < 791 then
              none
            else
              none
      else
        if v.val < 796 then
          if v.val < 794 then
            if v.val < 793 then
              none
            else
              none
          else
            if v.val < 795 then
              some ⟨⟨1534, by decide +kernel⟩, 2, some (24, 53)⟩
            else
              none
        else
          if v.val < 798 then
            if v.val < 797 then
              none
            else
              none
          else
            if v.val < 799 then
              none
            else
              none
  else
    if v.val < 816 then
      if v.val < 808 then
        if v.val < 804 then
          if v.val < 802 then
            if v.val < 801 then
              none
            else
              none
          else
            if v.val < 803 then
              none
            else
              none
        else
          if v.val < 806 then
            if v.val < 805 then
              some ⟨⟨806, by decide +kernel⟩, 2, some (25, 3)⟩
            else
              none
          else
            if v.val < 807 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (25, 23)⟩
            else
              some ⟨⟨809, by decide +kernel⟩, 2, some (25, 28)⟩
      else
        if v.val < 812 then
          if v.val < 810 then
            if v.val < 809 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (25, 30)⟩
          else
            if v.val < 811 then
              none
            else
              none
        else
          if v.val < 814 then
            if v.val < 813 then
              none
            else
              none
          else
            if v.val < 815 then
              none
            else
              none
    else
      if v.val < 824 then
        if v.val < 820 then
          if v.val < 818 then
            if v.val < 817 then
              none
            else
              none
          else
            if v.val < 819 then
              none
            else
              none
        else
          if v.val < 822 then
            if v.val < 821 then
              none
            else
              none
          else
            if v.val < 823 then
              none
            else
              some ⟨⟨1401, by decide +kernel⟩, 3, some (25, 44)⟩
      else
        if v.val < 828 then
          if v.val < 826 then
            if v.val < 825 then
              none
            else
              some ⟨⟨823, by decide +kernel⟩, 4, some (25, 48)⟩
          else
            if v.val < 827 then
              some ⟨⟨1554, by decide +kernel⟩, 3, some (25, 63)⟩
            else
              none
        else
          if v.val < 830 then
            if v.val < 829 then
              none
            else
              none
          else
            if v.val < 831 then
              none
            else
              none
def witnessBlock13 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 864 then
    if v.val < 848 then
      if v.val < 840 then
        if v.val < 836 then
          if v.val < 834 then
            if v.val < 833 then
              some ⟨⟨1574, by decide +kernel⟩, 4, some (26, 4)⟩
            else
              none
          else
            if v.val < 835 then
              none
            else
              none
        else
          if v.val < 838 then
            if v.val < 837 then
              none
            else
              some ⟨⟨832, by decide +kernel⟩, 5, some (26, 26)⟩
          else
            if v.val < 839 then
              some ⟨⟨823, by decide +kernel⟩, 4, some (26, 30)⟩
            else
              none
      else
        if v.val < 844 then
          if v.val < 842 then
            if v.val < 841 then
              none
            else
              none
          else
            if v.val < 843 then
              none
            else
              none
        else
          if v.val < 846 then
            if v.val < 845 then
              none
            else
              none
          else
            if v.val < 847 then
              none
            else
              none
    else
      if v.val < 856 then
        if v.val < 852 then
          if v.val < 850 then
            if v.val < 849 then
              none
            else
              none
          else
            if v.val < 851 then
              some ⟨⟨853, by decide +kernel⟩, 2, some (26, 50)⟩
            else
              none
        else
          if v.val < 854 then
            if v.val < 853 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (27, 10)⟩
          else
            if v.val < 855 then
              none
            else
              none
      else
        if v.val < 860 then
          if v.val < 858 then
            if v.val < 857 then
              none
            else
              none
          else
            if v.val < 859 then
              none
            else
              none
        else
          if v.val < 862 then
            if v.val < 861 then
              none
            else
              none
          else
            if v.val < 863 then
              none
            else
              none
  else
    if v.val < 880 then
      if v.val < 872 then
        if v.val < 868 then
          if v.val < 866 then
            if v.val < 865 then
              none
            else
              none
          else
            if v.val < 867 then
              none
            else
              none
        else
          if v.val < 870 then
            if v.val < 869 then
              none
            else
              none
          else
            if v.val < 871 then
              none
            else
              none
      else
        if v.val < 876 then
          if v.val < 874 then
            if v.val < 873 then
              none
            else
              none
          else
            if v.val < 875 then
              none
            else
              none
        else
          if v.val < 878 then
            if v.val < 877 then
              none
            else
              none
          else
            if v.val < 879 then
              some ⟨⟨879, by decide +kernel⟩, 2, some (27, 32)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (27, 41)⟩
    else
      if v.val < 888 then
        if v.val < 884 then
          if v.val < 882 then
            if v.val < 881 then
              none
            else
              none
          else
            if v.val < 883 then
              none
            else
              none
        else
          if v.val < 886 then
            if v.val < 885 then
              none
            else
              none
          else
            if v.val < 887 then
              none
            else
              none
      else
        if v.val < 892 then
          if v.val < 890 then
            if v.val < 889 then
              some ⟨⟨572, by decide +kernel⟩, 2, some (27, 58)⟩
            else
              none
          else
            if v.val < 891 then
              none
            else
              some ⟨⟨572, by decide +kernel⟩, 2, some (28, 3)⟩
        else
          if v.val < 894 then
            if v.val < 893 then
              none
            else
              none
          else
            if v.val < 895 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (28, 5)⟩
            else
              some ⟨⟨930, by decide +kernel⟩, 2, some (28, 6)⟩
def witnessBlock14 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 928 then
    if v.val < 912 then
      if v.val < 904 then
        if v.val < 900 then
          if v.val < 898 then
            if v.val < 897 then
              none
            else
              none
          else
            if v.val < 899 then
              some ⟨⟨930, by decide +kernel⟩, 2, some (28, 11)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (28, 15)⟩
        else
          if v.val < 902 then
            if v.val < 901 then
              some ⟨⟨930, by decide +kernel⟩, 2, some (28, 17)⟩
            else
              none
          else
            if v.val < 903 then
              some ⟨⟨930, by decide +kernel⟩, 2, some (28, 21)⟩
            else
              none
      else
        if v.val < 908 then
          if v.val < 906 then
            if v.val < 905 then
              none
            else
              some ⟨⟨900, by decide +kernel⟩, 3, some (28, 25)⟩
          else
            if v.val < 907 then
              none
            else
              none
        else
          if v.val < 910 then
            if v.val < 909 then
              some ⟨⟨930, by decide +kernel⟩, 2, some (28, 34)⟩
            else
              some ⟨⟨930, by decide +kernel⟩, 2, some (28, 36)⟩
          else
            if v.val < 911 then
              some ⟨⟨913, by decide +kernel⟩, 3, some (28, 39)⟩
            else
              none
    else
      if v.val < 920 then
        if v.val < 916 then
          if v.val < 914 then
            if v.val < 913 then
              none
            else
              some ⟨⟨930, by decide +kernel⟩, 2, some (28, 46)⟩
          else
            if v.val < 915 then
              none
            else
              some ⟨⟨930, by decide +kernel⟩, 2, some (28, 49)⟩
        else
          if v.val < 918 then
            if v.val < 917 then
              some ⟨⟨930, by decide +kernel⟩, 2, some (28, 50)⟩
            else
              none
          else
            if v.val < 919 then
              none
            else
              none
      else
        if v.val < 924 then
          if v.val < 922 then
            if v.val < 921 then
              some ⟨⟨930, by decide +kernel⟩, 2, some (28, 58)⟩
            else
              some ⟨⟨899, by decide +kernel⟩, 2, some (28, 61)⟩
          else
            if v.val < 923 then
              some ⟨⟨930, by decide +kernel⟩, 2, some (29, 8)⟩
            else
              none
        else
          if v.val < 926 then
            if v.val < 925 then
              none
            else
              some ⟨⟨853, by decide +kernel⟩, 2, some (29, 11)⟩
          else
            if v.val < 927 then
              some ⟨⟨930, by decide +kernel⟩, 2, some (29, 18)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (29, 23)⟩
  else
    if v.val < 944 then
      if v.val < 936 then
        if v.val < 932 then
          if v.val < 930 then
            if v.val < 929 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (29, 25)⟩
            else
              some ⟨⟨921, by decide +kernel⟩, 3, some (29, 29)⟩
          else
            if v.val < 931 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (29, 40)⟩
            else
              none
        else
          if v.val < 934 then
            if v.val < 933 then
              none
            else
              some ⟨⟨930, by decide +kernel⟩, 2, some (29, 50)⟩
          else
            if v.val < 935 then
              none
            else
              some ⟨⟨930, by decide +kernel⟩, 2, some (29, 53)⟩
      else
        if v.val < 940 then
          if v.val < 938 then
            if v.val < 937 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (29, 58)⟩
          else
            if v.val < 939 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (30, 2)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (30, 10)⟩
        else
          if v.val < 942 then
            if v.val < 941 then
              none
            else
              none
          else
            if v.val < 943 then
              none
            else
              none
    else
      if v.val < 952 then
        if v.val < 948 then
          if v.val < 946 then
            if v.val < 945 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (30, 17)⟩
          else
            if v.val < 947 then
              some ⟨⟨930, by decide +kernel⟩, 2, some (30, 21)⟩
            else
              some ⟨⟨945, by decide +kernel⟩, 2, some (30, 30)⟩
        else
          if v.val < 950 then
            if v.val < 949 then
              none
            else
              some ⟨⟨930, by decide +kernel⟩, 2, some (30, 31)⟩
          else
            if v.val < 951 then
              some ⟨⟨930, by decide +kernel⟩, 2, some (30, 32)⟩
            else
              some ⟨⟨930, by decide +kernel⟩, 2, some (30, 37)⟩
      else
        if v.val < 956 then
          if v.val < 954 then
            if v.val < 953 then
              some ⟨⟨1342, by decide +kernel⟩, 3, some (30, 44)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (30, 49)⟩
          else
            if v.val < 955 then
              some ⟨⟨930, by decide +kernel⟩, 2, some (30, 54)⟩
            else
              some ⟨⟨930, by decide +kernel⟩, 2, some (30, 56)⟩
        else
          if v.val < 958 then
            if v.val < 957 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (30, 59)⟩
            else
              some ⟨⟨930, by decide +kernel⟩, 2, some (30, 61)⟩
          else
            if v.val < 959 then
              none
            else
              none
def witnessBlock15 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 992 then
    if v.val < 976 then
      if v.val < 968 then
        if v.val < 964 then
          if v.val < 962 then
            if v.val < 961 then
              none
            else
              none
          else
            if v.val < 963 then
              none
            else
              none
        else
          if v.val < 966 then
            if v.val < 965 then
              none
            else
              none
          else
            if v.val < 967 then
              none
            else
              none
      else
        if v.val < 972 then
          if v.val < 970 then
            if v.val < 969 then
              none
            else
              none
          else
            if v.val < 971 then
              none
            else
              none
        else
          if v.val < 974 then
            if v.val < 973 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (31, 0)⟩
          else
            if v.val < 975 then
              none
            else
              none
    else
      if v.val < 984 then
        if v.val < 980 then
          if v.val < 978 then
            if v.val < 977 then
              none
            else
              none
          else
            if v.val < 979 then
              none
            else
              none
        else
          if v.val < 982 then
            if v.val < 981 then
              none
            else
              none
          else
            if v.val < 983 then
              none
            else
              none
      else
        if v.val < 988 then
          if v.val < 986 then
            if v.val < 985 then
              none
            else
              none
          else
            if v.val < 987 then
              none
            else
              none
        else
          if v.val < 990 then
            if v.val < 989 then
              none
            else
              none
          else
            if v.val < 991 then
              none
            else
              none
  else
    if v.val < 1008 then
      if v.val < 1000 then
        if v.val < 996 then
          if v.val < 994 then
            if v.val < 993 then
              none
            else
              none
          else
            if v.val < 995 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 0, none⟩
        else
          if v.val < 998 then
            if v.val < 997 then
              none
            else
              none
          else
            if v.val < 999 then
              none
            else
              none
      else
        if v.val < 1004 then
          if v.val < 1002 then
            if v.val < 1001 then
              none
            else
              none
          else
            if v.val < 1003 then
              none
            else
              none
        else
          if v.val < 1006 then
            if v.val < 1005 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (31, 7)⟩
            else
              none
          else
            if v.val < 1007 then
              none
            else
              none
    else
      if v.val < 1016 then
        if v.val < 1012 then
          if v.val < 1010 then
            if v.val < 1009 then
              some ⟨⟨1018, by decide +kernel⟩, 3, some (31, 17)⟩
            else
              some ⟨⟨1010, by decide +kernel⟩, 2, some (31, 18)⟩
          else
            if v.val < 1011 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (31, 22)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (31, 27)⟩
        else
          if v.val < 1014 then
            if v.val < 1013 then
              none
            else
              none
          else
            if v.val < 1015 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (31, 35)⟩
            else
              none
      else
        if v.val < 1020 then
          if v.val < 1018 then
            if v.val < 1017 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (31, 41)⟩
            else
              none
          else
            if v.val < 1019 then
              some ⟨⟨1010, by decide +kernel⟩, 2, some (31, 45)⟩
            else
              none
        else
          if v.val < 1022 then
            if v.val < 1021 then
              none
            else
              none
          else
            if v.val < 1023 then
              none
            else
              none
def witnessBlock16 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 1056 then
    if v.val < 1040 then
      if v.val < 1032 then
        if v.val < 1028 then
          if v.val < 1026 then
            if v.val < 1025 then
              none
            else
              none
          else
            if v.val < 1027 then
              none
            else
              none
        else
          if v.val < 1030 then
            if v.val < 1029 then
              none
            else
              some ⟨⟨905, by decide +kernel⟩, 4, some (31, 56)⟩
          else
            if v.val < 1031 then
              none
            else
              none
      else
        if v.val < 1036 then
          if v.val < 1034 then
            if v.val < 1033 then
              none
            else
              none
          else
            if v.val < 1035 then
              none
            else
              none
        else
          if v.val < 1038 then
            if v.val < 1037 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (32, 14)⟩
            else
              some ⟨⟨1039, by decide +kernel⟩, 2, some (32, 23)⟩
          else
            if v.val < 1039 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (32, 28)⟩
    else
      if v.val < 1048 then
        if v.val < 1044 then
          if v.val < 1042 then
            if v.val < 1041 then
              none
            else
              none
          else
            if v.val < 1043 then
              none
            else
              none
        else
          if v.val < 1046 then
            if v.val < 1045 then
              some ⟨⟨1050, by decide +kernel⟩, 2, some (32, 38)⟩
            else
              none
          else
            if v.val < 1047 then
              some ⟨⟨1051, by decide +kernel⟩, 2, some (32, 55)⟩
            else
              none
      else
        if v.val < 1052 then
          if v.val < 1050 then
            if v.val < 1049 then
              some ⟨⟨1051, by decide +kernel⟩, 2, some (32, 58)⟩
            else
              none
          else
            if v.val < 1051 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (32, 61)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (32, 63)⟩
        else
          if v.val < 1054 then
            if v.val < 1053 then
              none
            else
              none
          else
            if v.val < 1055 then
              none
            else
              none
  else
    if v.val < 1072 then
      if v.val < 1064 then
        if v.val < 1060 then
          if v.val < 1058 then
            if v.val < 1057 then
              none
            else
              none
          else
            if v.val < 1059 then
              none
            else
              none
        else
          if v.val < 1062 then
            if v.val < 1061 then
              none
            else
              some ⟨⟨1062, by decide +kernel⟩, 2, some (33, 5)⟩
          else
            if v.val < 1063 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (33, 6)⟩
            else
              some ⟨⟨1046, by decide +kernel⟩, 3, some (33, 7)⟩
      else
        if v.val < 1068 then
          if v.val < 1066 then
            if v.val < 1065 then
              none
            else
              none
          else
            if v.val < 1067 then
              none
            else
              none
        else
          if v.val < 1070 then
            if v.val < 1069 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (33, 16)⟩
          else
            if v.val < 1071 then
              none
            else
              none
    else
      if v.val < 1080 then
        if v.val < 1076 then
          if v.val < 1074 then
            if v.val < 1073 then
              none
            else
              none
          else
            if v.val < 1075 then
              none
            else
              none
        else
          if v.val < 1078 then
            if v.val < 1077 then
              none
            else
              none
          else
            if v.val < 1079 then
              none
            else
              none
      else
        if v.val < 1084 then
          if v.val < 1082 then
            if v.val < 1081 then
              none
            else
              some ⟨⟨1084, by decide +kernel⟩, 2, some (33, 31)⟩
          else
            if v.val < 1083 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (33, 32)⟩
        else
          if v.val < 1086 then
            if v.val < 1085 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (33, 36)⟩
            else
              some ⟨⟨1083, by decide +kernel⟩, 2, some (33, 40)⟩
          else
            if v.val < 1087 then
              none
            else
              none
def witnessBlock17 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 1120 then
    if v.val < 1104 then
      if v.val < 1096 then
        if v.val < 1092 then
          if v.val < 1090 then
            if v.val < 1089 then
              none
            else
              none
          else
            if v.val < 1091 then
              none
            else
              none
        else
          if v.val < 1094 then
            if v.val < 1093 then
              none
            else
              none
          else
            if v.val < 1095 then
              none
            else
              none
      else
        if v.val < 1100 then
          if v.val < 1098 then
            if v.val < 1097 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (33, 51)⟩
            else
              none
          else
            if v.val < 1099 then
              some ⟨⟨1195, by decide +kernel⟩, 3, some (33, 61)⟩
            else
              none
        else
          if v.val < 1102 then
            if v.val < 1101 then
              none
            else
              none
          else
            if v.val < 1103 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (34, 5)⟩
    else
      if v.val < 1112 then
        if v.val < 1108 then
          if v.val < 1106 then
            if v.val < 1105 then
              none
            else
              none
          else
            if v.val < 1107 then
              some ⟨⟨1108, by decide +kernel⟩, 2, some (34, 14)⟩
            else
              none
        else
          if v.val < 1110 then
            if v.val < 1109 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (34, 22)⟩
            else
              none
          else
            if v.val < 1111 then
              none
            else
              none
      else
        if v.val < 1116 then
          if v.val < 1114 then
            if v.val < 1113 then
              none
            else
              none
          else
            if v.val < 1115 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (34, 37)⟩
        else
          if v.val < 1118 then
            if v.val < 1117 then
              none
            else
              none
          else
            if v.val < 1119 then
              none
            else
              none
  else
    if v.val < 1136 then
      if v.val < 1128 then
        if v.val < 1124 then
          if v.val < 1122 then
            if v.val < 1121 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (34, 39)⟩
          else
            if v.val < 1123 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (34, 46)⟩
            else
              none
        else
          if v.val < 1126 then
            if v.val < 1125 then
              none
            else
              none
          else
            if v.val < 1127 then
              none
            else
              none
      else
        if v.val < 1132 then
          if v.val < 1130 then
            if v.val < 1129 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (35, 16)⟩
            else
              none
          else
            if v.val < 1131 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (35, 17)⟩
            else
              none
        else
          if v.val < 1134 then
            if v.val < 1133 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (35, 33)⟩
            else
              none
          else
            if v.val < 1135 then
              none
            else
              none
    else
      if v.val < 1144 then
        if v.val < 1140 then
          if v.val < 1138 then
            if v.val < 1137 then
              none
            else
              none
          else
            if v.val < 1139 then
              none
            else
              none
        else
          if v.val < 1142 then
            if v.val < 1141 then
              none
            else
              none
          else
            if v.val < 1143 then
              none
            else
              none
      else
        if v.val < 1148 then
          if v.val < 1146 then
            if v.val < 1145 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (35, 45)⟩
          else
            if v.val < 1147 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (35, 46)⟩
            else
              none
        else
          if v.val < 1150 then
            if v.val < 1149 then
              none
            else
              none
          else
            if v.val < 1151 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (35, 49)⟩
            else
              none
def witnessBlock18 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 1184 then
    if v.val < 1168 then
      if v.val < 1160 then
        if v.val < 1156 then
          if v.val < 1154 then
            if v.val < 1153 then
              none
            else
              none
          else
            if v.val < 1155 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (35, 62)⟩
            else
              none
        else
          if v.val < 1158 then
            if v.val < 1157 then
              none
            else
              none
          else
            if v.val < 1159 then
              none
            else
              none
      else
        if v.val < 1164 then
          if v.val < 1162 then
            if v.val < 1161 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (37, 29)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (37, 31)⟩
          else
            if v.val < 1163 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (37, 40)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (38, 15)⟩
        else
          if v.val < 1166 then
            if v.val < 1165 then
              none
            else
              none
          else
            if v.val < 1167 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (38, 29)⟩
            else
              none
    else
      if v.val < 1176 then
        if v.val < 1172 then
          if v.val < 1170 then
            if v.val < 1169 then
              none
            else
              none
          else
            if v.val < 1171 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (38, 38)⟩
            else
              some ⟨⟨1170, by decide +kernel⟩, 2, some (38, 45)⟩
        else
          if v.val < 1174 then
            if v.val < 1173 then
              none
            else
              none
          else
            if v.val < 1175 then
              none
            else
              none
      else
        if v.val < 1180 then
          if v.val < 1178 then
            if v.val < 1177 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (39, 0)⟩
            else
              some ⟨⟨1176, by decide +kernel⟩, 2, some (39, 4)⟩
          else
            if v.val < 1179 then
              some ⟨⟨1238, by decide +kernel⟩, 3, some (39, 5)⟩
            else
              some ⟨⟨1160, by decide +kernel⟩, 2, some (39, 9)⟩
        else
          if v.val < 1182 then
            if v.val < 1181 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (39, 14)⟩
          else
            if v.val < 1183 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (39, 21)⟩
  else
    if v.val < 1200 then
      if v.val < 1192 then
        if v.val < 1188 then
          if v.val < 1186 then
            if v.val < 1185 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (39, 27)⟩
            else
              some ⟨⟨1130, by decide +kernel⟩, 2, some (39, 30)⟩
          else
            if v.val < 1187 then
              none
            else
              none
        else
          if v.val < 1190 then
            if v.val < 1189 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (39, 36)⟩
            else
              none
          else
            if v.val < 1191 then
              none
            else
              none
      else
        if v.val < 1196 then
          if v.val < 1194 then
            if v.val < 1193 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (39, 42)⟩
            else
              none
          else
            if v.val < 1195 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (39, 45)⟩
            else
              some ⟨⟨1194, by decide +kernel⟩, 2, some (39, 47)⟩
        else
          if v.val < 1198 then
            if v.val < 1197 then
              none
            else
              none
          else
            if v.val < 1199 then
              none
            else
              some ⟨⟨1209, by decide +kernel⟩, 3, some (39, 54)⟩
    else
      if v.val < 1208 then
        if v.val < 1204 then
          if v.val < 1202 then
            if v.val < 1201 then
              none
            else
              none
          else
            if v.val < 1203 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (39, 56)⟩
        else
          if v.val < 1206 then
            if v.val < 1205 then
              some ⟨⟨1195, by decide +kernel⟩, 3, some (39, 59)⟩
            else
              none
          else
            if v.val < 1207 then
              none
            else
              none
      else
        if v.val < 1212 then
          if v.val < 1210 then
            if v.val < 1209 then
              none
            else
              some ⟨⟨1160, by decide +kernel⟩, 2, some (40, 3)⟩
          else
            if v.val < 1211 then
              none
            else
              some ⟨⟨1203, by decide +kernel⟩, 2, some (40, 9)⟩
        else
          if v.val < 1214 then
            if v.val < 1213 then
              none
            else
              none
          else
            if v.val < 1215 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (40, 12)⟩
def witnessBlock19 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 1248 then
    if v.val < 1232 then
      if v.val < 1224 then
        if v.val < 1220 then
          if v.val < 1218 then
            if v.val < 1217 then
              none
            else
              none
          else
            if v.val < 1219 then
              some ⟨⟨1219, by decide +kernel⟩, 2, some (40, 23)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (40, 27)⟩
        else
          if v.val < 1222 then
            if v.val < 1221 then
              some ⟨⟨1222, by decide +kernel⟩, 2, some (40, 35)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (40, 38)⟩
          else
            if v.val < 1223 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (40, 53)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (41, 23)⟩
      else
        if v.val < 1228 then
          if v.val < 1226 then
            if v.val < 1225 then
              none
            else
              none
          else
            if v.val < 1227 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (41, 48)⟩
        else
          if v.val < 1230 then
            if v.val < 1229 then
              some ⟨⟨1160, by decide +kernel⟩, 2, some (41, 56)⟩
            else
              none
          else
            if v.val < 1231 then
              none
            else
              none
    else
      if v.val < 1240 then
        if v.val < 1236 then
          if v.val < 1234 then
            if v.val < 1233 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (41, 60)⟩
          else
            if v.val < 1235 then
              some ⟨⟨1233, by decide +kernel⟩, 2, some (42, 4)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (42, 6)⟩
        else
          if v.val < 1238 then
            if v.val < 1237 then
              none
            else
              none
          else
            if v.val < 1239 then
              some ⟨⟨1160, by decide +kernel⟩, 2, some (42, 17)⟩
            else
              some ⟨⟨1176, by decide +kernel⟩, 2, some (42, 20)⟩
      else
        if v.val < 1244 then
          if v.val < 1242 then
            if v.val < 1241 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (42, 23)⟩
          else
            if v.val < 1243 then
              none
            else
              none
        else
          if v.val < 1246 then
            if v.val < 1245 then
              none
            else
              none
          else
            if v.val < 1247 then
              none
            else
              none
  else
    if v.val < 1264 then
      if v.val < 1256 then
        if v.val < 1252 then
          if v.val < 1250 then
            if v.val < 1249 then
              none
            else
              none
          else
            if v.val < 1251 then
              none
            else
              none
        else
          if v.val < 1254 then
            if v.val < 1253 then
              none
            else
              none
          else
            if v.val < 1255 then
              none
            else
              none
      else
        if v.val < 1260 then
          if v.val < 1258 then
            if v.val < 1257 then
              none
            else
              none
          else
            if v.val < 1259 then
              none
            else
              none
        else
          if v.val < 1262 then
            if v.val < 1261 then
              none
            else
              none
          else
            if v.val < 1263 then
              none
            else
              none
    else
      if v.val < 1272 then
        if v.val < 1268 then
          if v.val < 1266 then
            if v.val < 1265 then
              none
            else
              none
          else
            if v.val < 1267 then
              some ⟨⟨1271, by decide +kernel⟩, 3, some (43, 10)⟩
            else
              none
        else
          if v.val < 1270 then
            if v.val < 1269 then
              some ⟨⟨879, by decide +kernel⟩, 2, some (43, 11)⟩
            else
              none
          else
            if v.val < 1271 then
              some ⟨⟨572, by decide +kernel⟩, 2, some (43, 13)⟩
            else
              some ⟨⟨879, by decide +kernel⟩, 2, some (43, 19)⟩
      else
        if v.val < 1276 then
          if v.val < 1274 then
            if v.val < 1273 then
              some ⟨⟨1271, by decide +kernel⟩, 3, some (43, 24)⟩
            else
              some ⟨⟨1268, by decide +kernel⟩, 3, some (43, 27)⟩
          else
            if v.val < 1275 then
              some ⟨⟨879, by decide +kernel⟩, 2, some (43, 30)⟩
            else
              some ⟨⟨1295, by decide +kernel⟩, 2, some (43, 36)⟩
        else
          if v.val < 1278 then
            if v.val < 1277 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (43, 39)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (43, 51)⟩
          else
            if v.val < 1279 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (43, 56)⟩
def witnessBlock20 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 1312 then
    if v.val < 1296 then
      if v.val < 1288 then
        if v.val < 1284 then
          if v.val < 1282 then
            if v.val < 1281 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (44, 20)⟩
          else
            if v.val < 1283 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (44, 26)⟩
            else
              none
        else
          if v.val < 1286 then
            if v.val < 1285 then
              none
            else
              none
          else
            if v.val < 1287 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (44, 34)⟩
            else
              none
      else
        if v.val < 1292 then
          if v.val < 1290 then
            if v.val < 1289 then
              none
            else
              some ⟨⟨853, by decide +kernel⟩, 2, some (44, 37)⟩
          else
            if v.val < 1291 then
              none
            else
              some ⟨⟨572, by decide +kernel⟩, 2, some (44, 51)⟩
        else
          if v.val < 1294 then
            if v.val < 1293 then
              some ⟨⟨853, by decide +kernel⟩, 2, some (45, 12)⟩
            else
              some ⟨⟨1279, by decide +kernel⟩, 2, some (45, 17)⟩
          else
            if v.val < 1295 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (45, 26)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (45, 30)⟩
    else
      if v.val < 1304 then
        if v.val < 1300 then
          if v.val < 1298 then
            if v.val < 1297 then
              none
            else
              none
          else
            if v.val < 1299 then
              none
            else
              some ⟨⟨1300, by decide +kernel⟩, 3, some (45, 36)⟩
        else
          if v.val < 1302 then
            if v.val < 1301 then
              some ⟨⟨1295, by decide +kernel⟩, 2, some (45, 39)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (45, 58)⟩
          else
            if v.val < 1303 then
              none
            else
              none
      else
        if v.val < 1308 then
          if v.val < 1306 then
            if v.val < 1305 then
              none
            else
              none
          else
            if v.val < 1307 then
              none
            else
              none
        else
          if v.val < 1310 then
            if v.val < 1309 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (46, 30)⟩
          else
            if v.val < 1311 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (46, 31)⟩
            else
              some ⟨⟨1295, by decide +kernel⟩, 2, some (46, 33)⟩
  else
    if v.val < 1328 then
      if v.val < 1320 then
        if v.val < 1316 then
          if v.val < 1314 then
            if v.val < 1313 then
              none
            else
              none
          else
            if v.val < 1315 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (46, 41)⟩
            else
              none
        else
          if v.val < 1318 then
            if v.val < 1317 then
              none
            else
              some ⟨⟨1294, by decide +kernel⟩, 2, some (47, 8)⟩
          else
            if v.val < 1319 then
              none
            else
              none
      else
        if v.val < 1324 then
          if v.val < 1322 then
            if v.val < 1321 then
              none
            else
              none
          else
            if v.val < 1323 then
              none
            else
              none
        else
          if v.val < 1326 then
            if v.val < 1325 then
              none
            else
              none
          else
            if v.val < 1327 then
              none
            else
              none
    else
      if v.val < 1336 then
        if v.val < 1332 then
          if v.val < 1330 then
            if v.val < 1329 then
              none
            else
              none
          else
            if v.val < 1331 then
              none
            else
              none
        else
          if v.val < 1334 then
            if v.val < 1333 then
              none
            else
              none
          else
            if v.val < 1335 then
              none
            else
              none
      else
        if v.val < 1340 then
          if v.val < 1338 then
            if v.val < 1337 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (48, 19)⟩
          else
            if v.val < 1339 then
              none
            else
              none
        else
          if v.val < 1342 then
            if v.val < 1341 then
              none
            else
              none
          else
            if v.val < 1343 then
              some ⟨⟨853, by decide +kernel⟩, 2, some (48, 25)⟩
            else
              none
def witnessBlock21 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 1376 then
    if v.val < 1360 then
      if v.val < 1352 then
        if v.val < 1348 then
          if v.val < 1346 then
            if v.val < 1345 then
              none
            else
              none
          else
            if v.val < 1347 then
              none
            else
              none
        else
          if v.val < 1350 then
            if v.val < 1349 then
              none
            else
              none
          else
            if v.val < 1351 then
              none
            else
              none
      else
        if v.val < 1356 then
          if v.val < 1354 then
            if v.val < 1353 then
              none
            else
              none
          else
            if v.val < 1355 then
              none
            else
              none
        else
          if v.val < 1358 then
            if v.val < 1357 then
              none
            else
              none
          else
            if v.val < 1359 then
              none
            else
              none
    else
      if v.val < 1368 then
        if v.val < 1364 then
          if v.val < 1362 then
            if v.val < 1361 then
              none
            else
              none
          else
            if v.val < 1363 then
              none
            else
              none
        else
          if v.val < 1366 then
            if v.val < 1365 then
              none
            else
              none
          else
            if v.val < 1367 then
              none
            else
              none
      else
        if v.val < 1372 then
          if v.val < 1370 then
            if v.val < 1369 then
              none
            else
              none
          else
            if v.val < 1371 then
              none
            else
              none
        else
          if v.val < 1374 then
            if v.val < 1373 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (49, 35)⟩
          else
            if v.val < 1375 then
              some ⟨⟨703, by decide +kernel⟩, 2, some (49, 38)⟩
            else
              none
  else
    if v.val < 1392 then
      if v.val < 1384 then
        if v.val < 1380 then
          if v.val < 1378 then
            if v.val < 1377 then
              none
            else
              none
          else
            if v.val < 1379 then
              some ⟨⟨1233, by decide +kernel⟩, 2, some (49, 43)⟩
            else
              some ⟨⟨1382, by decide +kernel⟩, 2, some (49, 53)⟩
        else
          if v.val < 1382 then
            if v.val < 1381 then
              none
            else
              none
          else
            if v.val < 1383 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (49, 60)⟩
            else
              none
      else
        if v.val < 1388 then
          if v.val < 1386 then
            if v.val < 1385 then
              none
            else
              none
          else
            if v.val < 1387 then
              none
            else
              none
        else
          if v.val < 1390 then
            if v.val < 1389 then
              none
            else
              none
          else
            if v.val < 1391 then
              none
            else
              none
    else
      if v.val < 1400 then
        if v.val < 1396 then
          if v.val < 1394 then
            if v.val < 1393 then
              none
            else
              some ⟨⟨1406, by decide +kernel⟩, 2, some (50, 13)⟩
          else
            if v.val < 1395 then
              none
            else
              none
        else
          if v.val < 1398 then
            if v.val < 1397 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (50, 19)⟩
            else
              some ⟨⟨1396, by decide +kernel⟩, 2, some (50, 23)⟩
          else
            if v.val < 1399 then
              some ⟨⟨1396, by decide +kernel⟩, 2, some (50, 30)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (50, 34)⟩
      else
        if v.val < 1404 then
          if v.val < 1402 then
            if v.val < 1401 then
              some ⟨⟨1396, by decide +kernel⟩, 2, some (50, 36)⟩
            else
              some ⟨⟨1396, by decide +kernel⟩, 2, some (50, 38)⟩
          else
            if v.val < 1403 then
              none
            else
              some ⟨⟨1574, by decide +kernel⟩, 4, some (50, 41)⟩
        else
          if v.val < 1406 then
            if v.val < 1405 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (50, 43)⟩
          else
            if v.val < 1407 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (50, 53)⟩
            else
              none
def witnessBlock22 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 1440 then
    if v.val < 1424 then
      if v.val < 1416 then
        if v.val < 1412 then
          if v.val < 1410 then
            if v.val < 1409 then
              none
            else
              none
          else
            if v.val < 1411 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (50, 63)⟩
            else
              none
        else
          if v.val < 1414 then
            if v.val < 1413 then
              none
            else
              none
          else
            if v.val < 1415 then
              none
            else
              some ⟨⟨1062, by decide +kernel⟩, 2, some (51, 11)⟩
      else
        if v.val < 1420 then
          if v.val < 1418 then
            if v.val < 1417 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (51, 13)⟩
            else
              none
          else
            if v.val < 1419 then
              none
            else
              none
        else
          if v.val < 1422 then
            if v.val < 1421 then
              none
            else
              none
          else
            if v.val < 1423 then
              none
            else
              none
    else
      if v.val < 1432 then
        if v.val < 1428 then
          if v.val < 1426 then
            if v.val < 1425 then
              none
            else
              none
          else
            if v.val < 1427 then
              none
            else
              some ⟨⟨1183, by decide +kernel⟩, 2, some (51, 44)⟩
        else
          if v.val < 1430 then
            if v.val < 1429 then
              none
            else
              none
          else
            if v.val < 1431 then
              none
            else
              none
      else
        if v.val < 1436 then
          if v.val < 1434 then
            if v.val < 1433 then
              some ⟨⟨1466, by decide +kernel⟩, 3, some (51, 51)⟩
            else
              none
          else
            if v.val < 1435 then
              none
            else
              none
        else
          if v.val < 1438 then
            if v.val < 1437 then
              none
            else
              none
          else
            if v.val < 1439 then
              none
            else
              none
  else
    if v.val < 1456 then
      if v.val < 1448 then
        if v.val < 1444 then
          if v.val < 1442 then
            if v.val < 1441 then
              none
            else
              some ⟨⟨1108, by decide +kernel⟩, 2, some (51, 63)⟩
          else
            if v.val < 1443 then
              none
            else
              none
        else
          if v.val < 1446 then
            if v.val < 1445 then
              some ⟨⟨1130, by decide +kernel⟩, 2, some (52, 5)⟩
            else
              none
          else
            if v.val < 1447 then
              none
            else
              none
      else
        if v.val < 1452 then
          if v.val < 1450 then
            if v.val < 1449 then
              none
            else
              none
          else
            if v.val < 1451 then
              none
            else
              some ⟨⟨1401, by decide +kernel⟩, 3, some (52, 25)⟩
        else
          if v.val < 1454 then
            if v.val < 1453 then
              none
            else
              none
          else
            if v.val < 1455 then
              none
            else
              none
    else
      if v.val < 1464 then
        if v.val < 1460 then
          if v.val < 1458 then
            if v.val < 1457 then
              none
            else
              some ⟨⟨1215, by decide +kernel⟩, 2, some (52, 47)⟩
          else
            if v.val < 1459 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (52, 55)⟩
            else
              some ⟨⟨973, by decide +kernel⟩, 2, some (53, 1)⟩
        else
          if v.val < 1462 then
            if v.val < 1461 then
              none
            else
              none
          else
            if v.val < 1463 then
              none
            else
              some ⟨⟨1466, by decide +kernel⟩, 3, some (53, 6)⟩
      else
        if v.val < 1468 then
          if v.val < 1466 then
            if v.val < 1465 then
              none
            else
              none
          else
            if v.val < 1467 then
              some ⟨⟨973, by decide +kernel⟩, 2, some (53, 14)⟩
            else
              none
        else
          if v.val < 1470 then
            if v.val < 1469 then
              none
            else
              some ⟨⟨1466, by decide +kernel⟩, 3, some (53, 31)⟩
          else
            if v.val < 1471 then
              some ⟨⟨1463, by decide +kernel⟩, 4, some (53, 35)⟩
            else
              some ⟨⟨1470, by decide +kernel⟩, 5, some (53, 37)⟩
def witnessBlock23 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 1504 then
    if v.val < 1488 then
      if v.val < 1480 then
        if v.val < 1476 then
          if v.val < 1474 then
            if v.val < 1473 then
              none
            else
              none
          else
            if v.val < 1475 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (53, 44)⟩
            else
              none
        else
          if v.val < 1478 then
            if v.val < 1477 then
              none
            else
              none
          else
            if v.val < 1479 then
              none
            else
              none
      else
        if v.val < 1484 then
          if v.val < 1482 then
            if v.val < 1481 then
              none
            else
              none
          else
            if v.val < 1483 then
              none
            else
              none
        else
          if v.val < 1486 then
            if v.val < 1485 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (54, 2)⟩
          else
            if v.val < 1487 then
              none
            else
              none
    else
      if v.val < 1496 then
        if v.val < 1492 then
          if v.val < 1490 then
            if v.val < 1489 then
              none
            else
              none
          else
            if v.val < 1491 then
              none
            else
              none
        else
          if v.val < 1494 then
            if v.val < 1493 then
              none
            else
              none
          else
            if v.val < 1495 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (55, 45)⟩
      else
        if v.val < 1500 then
          if v.val < 1498 then
            if v.val < 1497 then
              none
            else
              none
          else
            if v.val < 1499 then
              none
            else
              none
        else
          if v.val < 1502 then
            if v.val < 1501 then
              none
            else
              none
          else
            if v.val < 1503 then
              none
            else
              none
  else
    if v.val < 1520 then
      if v.val < 1512 then
        if v.val < 1508 then
          if v.val < 1506 then
            if v.val < 1505 then
              some ⟨⟨1301, by decide +kernel⟩, 2, some (56, 27)⟩
            else
              some ⟨⟨1046, by decide +kernel⟩, 3, some (56, 33)⟩
          else
            if v.val < 1507 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (56, 36)⟩
        else
          if v.val < 1510 then
            if v.val < 1509 then
              none
            else
              none
          else
            if v.val < 1511 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (56, 40)⟩
            else
              none
      else
        if v.val < 1516 then
          if v.val < 1514 then
            if v.val < 1513 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (56, 50)⟩
          else
            if v.val < 1515 then
              none
            else
              none
        else
          if v.val < 1518 then
            if v.val < 1517 then
              none
            else
              none
          else
            if v.val < 1519 then
              none
            else
              none
    else
      if v.val < 1528 then
        if v.val < 1524 then
          if v.val < 1522 then
            if v.val < 1521 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (56, 61)⟩
            else
              none
          else
            if v.val < 1523 then
              none
            else
              none
        else
          if v.val < 1526 then
            if v.val < 1525 then
              none
            else
              none
          else
            if v.val < 1527 then
              none
            else
              some ⟨⟨1295, by decide +kernel⟩, 2, some (57, 21)⟩
      else
        if v.val < 1532 then
          if v.val < 1530 then
            if v.val < 1529 then
              none
            else
              none
          else
            if v.val < 1531 then
              none
            else
              none
        else
          if v.val < 1534 then
            if v.val < 1533 then
              none
            else
              none
          else
            if v.val < 1535 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (57, 36)⟩
            else
              none
def witnessBlock24 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 1568 then
    if v.val < 1552 then
      if v.val < 1544 then
        if v.val < 1540 then
          if v.val < 1538 then
            if v.val < 1537 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (57, 43)⟩
          else
            if v.val < 1539 then
              none
            else
              none
        else
          if v.val < 1542 then
            if v.val < 1541 then
              some ⟨⟨1222, by decide +kernel⟩, 2, some (57, 49)⟩
            else
              none
          else
            if v.val < 1543 then
              none
            else
              none
      else
        if v.val < 1548 then
          if v.val < 1546 then
            if v.val < 1545 then
              none
            else
              none
          else
            if v.val < 1547 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (57, 53)⟩
        else
          if v.val < 1550 then
            if v.val < 1549 then
              none
            else
              none
          else
            if v.val < 1551 then
              none
            else
              some ⟨⟨1145, by decide +kernel⟩, 2, some (57, 63)⟩
    else
      if v.val < 1560 then
        if v.val < 1556 then
          if v.val < 1554 then
            if v.val < 1553 then
              some ⟨⟨1219, by decide +kernel⟩, 2, some (58, 7)⟩
            else
              none
          else
            if v.val < 1555 then
              some ⟨⟨1223, by decide +kernel⟩, 2, some (58, 13)⟩
            else
              some ⟨⟨1220, by decide +kernel⟩, 3, some (58, 15)⟩
        else
          if v.val < 1558 then
            if v.val < 1557 then
              none
            else
              none
          else
            if v.val < 1559 then
              none
            else
              none
      else
        if v.val < 1564 then
          if v.val < 1562 then
            if v.val < 1561 then
              none
            else
              none
          else
            if v.val < 1563 then
              none
            else
              none
        else
          if v.val < 1566 then
            if v.val < 1565 then
              none
            else
              none
          else
            if v.val < 1567 then
              none
            else
              some ⟨⟨930, by decide +kernel⟩, 2, some (58, 39)⟩
  else
    if v.val < 1584 then
      if v.val < 1576 then
        if v.val < 1572 then
          if v.val < 1570 then
            if v.val < 1569 then
              some ⟨⟨930, by decide +kernel⟩, 2, some (58, 43)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (58, 46)⟩
          else
            if v.val < 1571 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (58, 52)⟩
        else
          if v.val < 1574 then
            if v.val < 1573 then
              some ⟨⟨1571, by decide +kernel⟩, 2, some (58, 59)⟩
            else
              none
          else
            if v.val < 1575 then
              some ⟨⟨1401, by decide +kernel⟩, 3, some (58, 63)⟩
            else
              none
      else
        if v.val < 1580 then
          if v.val < 1578 then
            if v.val < 1577 then
              none
            else
              none
          else
            if v.val < 1579 then
              none
            else
              some ⟨⟨1401, by decide +kernel⟩, 3, some (59, 9)⟩
        else
          if v.val < 1582 then
            if v.val < 1581 then
              none
            else
              none
          else
            if v.val < 1583 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (59, 18)⟩
    else
      if v.val < 1592 then
        if v.val < 1588 then
          if v.val < 1586 then
            if v.val < 1585 then
              none
            else
              none
          else
            if v.val < 1587 then
              some ⟨⟨1223, by decide +kernel⟩, 2, some (59, 60)⟩
            else
              none
        else
          if v.val < 1590 then
            if v.val < 1589 then
              none
            else
              none
          else
            if v.val < 1591 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (59, 63)⟩
            else
              some ⟨⟨1590, by decide +kernel⟩, 2, some (60, 2)⟩
      else
        if v.val < 1596 then
          if v.val < 1594 then
            if v.val < 1593 then
              none
            else
              none
          else
            if v.val < 1595 then
              none
            else
              none
        else
          if v.val < 1598 then
            if v.val < 1597 then
              none
            else
              none
          else
            if v.val < 1599 then
              none
            else
              none
def witnessBlock25 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 1632 then
    if v.val < 1616 then
      if v.val < 1608 then
        if v.val < 1604 then
          if v.val < 1602 then
            if v.val < 1601 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (60, 11)⟩
            else
              none
          else
            if v.val < 1603 then
              none
            else
              some ⟨⟨1718, by decide +kernel⟩, 2, some (60, 33)⟩
        else
          if v.val < 1606 then
            if v.val < 1605 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (60, 41)⟩
            else
              none
          else
            if v.val < 1607 then
              some ⟨⟨1608, by decide +kernel⟩, 2, some (60, 48)⟩
            else
              some ⟨⟨1608, by decide +kernel⟩, 2, some (60, 51)⟩
      else
        if v.val < 1612 then
          if v.val < 1610 then
            if v.val < 1609 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (60, 53)⟩
            else
              some ⟨⟨1704, by decide +kernel⟩, 2, some (60, 58)⟩
          else
            if v.val < 1611 then
              none
            else
              none
        else
          if v.val < 1614 then
            if v.val < 1613 then
              some ⟨⟨584, by decide +kernel⟩, 2, some (60, 60)⟩
            else
              none
          else
            if v.val < 1615 then
              none
            else
              none
    else
      if v.val < 1624 then
        if v.val < 1620 then
          if v.val < 1618 then
            if v.val < 1617 then
              none
            else
              none
          else
            if v.val < 1619 then
              none
            else
              none
        else
          if v.val < 1622 then
            if v.val < 1621 then
              some ⟨⟨928, by decide +kernel⟩, 2, some (61, 3)⟩
            else
              none
          else
            if v.val < 1623 then
              none
            else
              none
      else
        if v.val < 1628 then
          if v.val < 1626 then
            if v.val < 1625 then
              none
            else
              none
          else
            if v.val < 1627 then
              some ⟨⟨1396, by decide +kernel⟩, 2, some (61, 15)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (61, 17)⟩
        else
          if v.val < 1630 then
            if v.val < 1629 then
              none
            else
              none
          else
            if v.val < 1631 then
              none
            else
              none
  else
    if v.val < 1648 then
      if v.val < 1640 then
        if v.val < 1636 then
          if v.val < 1634 then
            if v.val < 1633 then
              none
            else
              some ⟨⟨1634, by decide +kernel⟩, 2, some (61, 34)⟩
          else
            if v.val < 1635 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (61, 36)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (61, 42)⟩
        else
          if v.val < 1638 then
            if v.val < 1637 then
              none
            else
              none
          else
            if v.val < 1639 then
              none
            else
              none
      else
        if v.val < 1644 then
          if v.val < 1642 then
            if v.val < 1641 then
              none
            else
              none
          else
            if v.val < 1643 then
              none
            else
              none
        else
          if v.val < 1646 then
            if v.val < 1645 then
              none
            else
              none
          else
            if v.val < 1647 then
              none
            else
              none
    else
      if v.val < 1656 then
        if v.val < 1652 then
          if v.val < 1650 then
            if v.val < 1649 then
              none
            else
              some ⟨⟨1406, by decide +kernel⟩, 2, some (61, 56)⟩
          else
            if v.val < 1651 then
              none
            else
              some ⟨⟨1396, by decide +kernel⟩, 2, some (62, 6)⟩
        else
          if v.val < 1654 then
            if v.val < 1653 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (62, 9)⟩
            else
              none
          else
            if v.val < 1655 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (62, 39)⟩
            else
              none
      else
        if v.val < 1660 then
          if v.val < 1658 then
            if v.val < 1657 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (63, 1)⟩
            else
              some ⟨⟨1649, by decide +kernel⟩, 3, some (63, 7)⟩
          else
            if v.val < 1659 then
              none
            else
              none
        else
          if v.val < 1662 then
            if v.val < 1661 then
              none
            else
              none
          else
            if v.val < 1663 then
              none
            else
              none
def witnessBlock26 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 1696 then
    if v.val < 1680 then
      if v.val < 1672 then
        if v.val < 1668 then
          if v.val < 1666 then
            if v.val < 1665 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (63, 15)⟩
          else
            if v.val < 1667 then
              none
            else
              some ⟨⟨1579, by decide +kernel⟩, 4, some (63, 21)⟩
        else
          if v.val < 1670 then
            if v.val < 1669 then
              some ⟨⟨1406, by decide +kernel⟩, 2, some (63, 27)⟩
            else
              some ⟨⟨1667, by decide +kernel⟩, 5, some (63, 36)⟩
          else
            if v.val < 1671 then
              none
            else
              none
      else
        if v.val < 1676 then
          if v.val < 1674 then
            if v.val < 1673 then
              none
            else
              none
          else
            if v.val < 1675 then
              none
            else
              none
        else
          if v.val < 1678 then
            if v.val < 1677 then
              none
            else
              none
          else
            if v.val < 1679 then
              none
            else
              some ⟨⟨1069, by decide +kernel⟩, 2, some (63, 47)⟩
    else
      if v.val < 1688 then
        if v.val < 1684 then
          if v.val < 1682 then
            if v.val < 1681 then
              none
            else
              none
          else
            if v.val < 1683 then
              none
            else
              some ⟨⟨1406, by decide +kernel⟩, 2, some (63, 54)⟩
        else
          if v.val < 1686 then
            if v.val < 1685 then
              none
            else
              none
          else
            if v.val < 1687 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (64, 0)⟩
      else
        if v.val < 1692 then
          if v.val < 1690 then
            if v.val < 1689 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (64, 3)⟩
          else
            if v.val < 1691 then
              none
            else
              some ⟨⟨1301, by decide +kernel⟩, 2, some (64, 11)⟩
        else
          if v.val < 1694 then
            if v.val < 1693 then
              none
            else
              none
          else
            if v.val < 1695 then
              none
            else
              none
  else
    if v.val < 1712 then
      if v.val < 1704 then
        if v.val < 1700 then
          if v.val < 1698 then
            if v.val < 1697 then
              none
            else
              none
          else
            if v.val < 1699 then
              none
            else
              none
        else
          if v.val < 1702 then
            if v.val < 1701 then
              none
            else
              none
          else
            if v.val < 1703 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (64, 21)⟩
            else
              none
      else
        if v.val < 1708 then
          if v.val < 1706 then
            if v.val < 1705 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (64, 25)⟩
            else
              none
          else
            if v.val < 1707 then
              none
            else
              some ⟨⟨1457, by decide +kernel⟩, 3, some (64, 30)⟩
        else
          if v.val < 1710 then
            if v.val < 1709 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (64, 31)⟩
            else
              none
          else
            if v.val < 1711 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (64, 38)⟩
            else
              none
    else
      if v.val < 1720 then
        if v.val < 1716 then
          if v.val < 1714 then
            if v.val < 1713 then
              none
            else
              some ⟨⟨1401, by decide +kernel⟩, 3, some (64, 46)⟩
          else
            if v.val < 1715 then
              some ⟨⟨1228, by decide +kernel⟩, 3, some (64, 52)⟩
            else
              some ⟨⟨1227, by decide +kernel⟩, 2, some (64, 55)⟩
        else
          if v.val < 1718 then
            if v.val < 1717 then
              none
            else
              none
          else
            if v.val < 1719 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (64, 63)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (65, 9)⟩
      else
        if v.val < 1724 then
          if v.val < 1722 then
            if v.val < 1721 then
              none
            else
              none
          else
            if v.val < 1723 then
              none
            else
              some ⟨⟨1734, by decide +kernel⟩, 3, some (65, 32)⟩
        else
          if v.val < 1726 then
            if v.val < 1725 then
              none
            else
              none
          else
            if v.val < 1727 then
              some ⟨⟨1398, by decide +kernel⟩, 3, some (65, 39)⟩
            else
              none
def witnessBlock27 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 1760 then
    if v.val < 1744 then
      if v.val < 1736 then
        if v.val < 1732 then
          if v.val < 1730 then
            if v.val < 1729 then
              none
            else
              some ⟨⟨1634, by decide +kernel⟩, 2, some (65, 53)⟩
          else
            if v.val < 1731 then
              none
            else
              none
        else
          if v.val < 1734 then
            if v.val < 1733 then
              some ⟨⟨1555, by decide +kernel⟩, 4, some (66, 10)⟩
            else
              none
          else
            if v.val < 1735 then
              some ⟨⟨1223, by decide +kernel⟩, 2, some (66, 12)⟩
            else
              none
      else
        if v.val < 1740 then
          if v.val < 1738 then
            if v.val < 1737 then
              some ⟨⟨1537, by decide +kernel⟩, 2, some (66, 18)⟩
            else
              none
          else
            if v.val < 1739 then
              none
            else
              none
        else
          if v.val < 1742 then
            if v.val < 1741 then
              none
            else
              none
          else
            if v.val < 1743 then
              none
            else
              none
    else
      if v.val < 1752 then
        if v.val < 1748 then
          if v.val < 1746 then
            if v.val < 1745 then
              none
            else
              none
          else
            if v.val < 1747 then
              none
            else
              none
        else
          if v.val < 1750 then
            if v.val < 1749 then
              none
            else
              none
          else
            if v.val < 1751 then
              none
            else
              none
      else
        if v.val < 1756 then
          if v.val < 1754 then
            if v.val < 1753 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (66, 49)⟩
          else
            if v.val < 1755 then
              none
            else
              none
        else
          if v.val < 1758 then
            if v.val < 1757 then
              none
            else
              none
          else
            if v.val < 1759 then
              none
            else
              none
  else
    if v.val < 1776 then
      if v.val < 1768 then
        if v.val < 1764 then
          if v.val < 1762 then
            if v.val < 1761 then
              none
            else
              none
          else
            if v.val < 1763 then
              none
            else
              none
        else
          if v.val < 1766 then
            if v.val < 1765 then
              none
            else
              none
          else
            if v.val < 1767 then
              none
            else
              none
      else
        if v.val < 1772 then
          if v.val < 1770 then
            if v.val < 1769 then
              none
            else
              none
          else
            if v.val < 1771 then
              none
            else
              none
        else
          if v.val < 1774 then
            if v.val < 1773 then
              none
            else
              none
          else
            if v.val < 1775 then
              none
            else
              none
    else
      if v.val < 1784 then
        if v.val < 1780 then
          if v.val < 1778 then
            if v.val < 1777 then
              none
            else
              none
          else
            if v.val < 1779 then
              none
            else
              none
        else
          if v.val < 1782 then
            if v.val < 1781 then
              none
            else
              none
          else
            if v.val < 1783 then
              none
            else
              none
      else
        if v.val < 1788 then
          if v.val < 1786 then
            if v.val < 1785 then
              none
            else
              none
          else
            if v.val < 1787 then
              none
            else
              none
        else
          if v.val < 1790 then
            if v.val < 1789 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (67, 19)⟩
            else
              none
          else
            if v.val < 1791 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (67, 24)⟩
            else
              none
def witnessBlock28 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 1824 then
    if v.val < 1808 then
      if v.val < 1800 then
        if v.val < 1796 then
          if v.val < 1794 then
            if v.val < 1793 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (67, 25)⟩
            else
              none
          else
            if v.val < 1795 then
              none
            else
              none
        else
          if v.val < 1798 then
            if v.val < 1797 then
              none
            else
              none
          else
            if v.val < 1799 then
              none
            else
              none
      else
        if v.val < 1804 then
          if v.val < 1802 then
            if v.val < 1801 then
              none
            else
              none
          else
            if v.val < 1803 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (67, 31)⟩
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (67, 34)⟩
        else
          if v.val < 1806 then
            if v.val < 1805 then
              some ⟨⟨1803, by decide +kernel⟩, 2, some (67, 36)⟩
            else
              none
          else
            if v.val < 1807 then
              none
            else
              none
    else
      if v.val < 1816 then
        if v.val < 1812 then
          if v.val < 1810 then
            if v.val < 1809 then
              none
            else
              none
          else
            if v.val < 1811 then
              none
            else
              none
        else
          if v.val < 1814 then
            if v.val < 1813 then
              none
            else
              none
          else
            if v.val < 1815 then
              none
            else
              none
      else
        if v.val < 1820 then
          if v.val < 1818 then
            if v.val < 1817 then
              none
            else
              none
          else
            if v.val < 1819 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (67, 49)⟩
        else
          if v.val < 1822 then
            if v.val < 1821 then
              none
            else
              none
          else
            if v.val < 1823 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (67, 53)⟩
  else
    if v.val < 1840 then
      if v.val < 1832 then
        if v.val < 1828 then
          if v.val < 1826 then
            if v.val < 1825 then
              none
            else
              none
          else
            if v.val < 1827 then
              none
            else
              none
        else
          if v.val < 1830 then
            if v.val < 1829 then
              none
            else
              none
          else
            if v.val < 1831 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (67, 62)⟩
      else
        if v.val < 1836 then
          if v.val < 1834 then
            if v.val < 1833 then
              some ⟨⟨995, by decide +kernel⟩, 1, some (67, 63)⟩
            else
              some ⟨⟨1832, by decide +kernel⟩, 2, some (68, 12)⟩
          else
            if v.val < 1835 then
              none
            else
              none
        else
          if v.val < 1838 then
            if v.val < 1837 then
              some ⟨⟨1839, by decide +kernel⟩, 3, some (68, 25)⟩
            else
              none
          else
            if v.val < 1839 then
              none
            else
              some ⟨⟨1819, by decide +kernel⟩, 2, some (68, 36)⟩
    else
      if v.val < 1848 then
        if v.val < 1844 then
          if v.val < 1842 then
            if v.val < 1841 then
              none
            else
              none
          else
            if v.val < 1843 then
              none
            else
              none
        else
          if v.val < 1846 then
            if v.val < 1845 then
              some ⟨⟨645, by decide +kernel⟩, 2, some (68, 42)⟩
            else
              none
          else
            if v.val < 1847 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (68, 44)⟩
      else
        if v.val < 1852 then
          if v.val < 1850 then
            if v.val < 1849 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (68, 48)⟩
          else
            if v.val < 1851 then
              none
            else
              some ⟨⟨995, by decide +kernel⟩, 1, some (68, 51)⟩
        else
          if v.val < 1854 then
            if v.val < 1853 then
              none
            else
              none
          else
            if v.val < 1855 then
              none
            else
              none
def witnessBlock29 (v : Fin 1864) : Option (EnhancedWitness 1864) :=
  if v.val < 1860 then
    if v.val < 1858 then
      if v.val < 1857 then
        none
      else
        none
    else
      if v.val < 1859 then
        some ⟨⟨995, by decide +kernel⟩, 1, some (68, 61)⟩
      else
        none
  else
    if v.val < 1862 then
      if v.val < 1861 then
        none
      else
        none
    else
      if v.val < 1863 then
        none
      else
        none
def certificate : EnhancedCertificate 1864 := ⟨fun v =>
  if v.val < 960 then
    if v.val < 448 then
      if v.val < 192 then
        if v.val < 64 then
          witnessBlock0 v
        else
          if v.val < 128 then
            witnessBlock1 v
          else
            witnessBlock2 v
      else
        if v.val < 320 then
          if v.val < 256 then
            witnessBlock3 v
          else
            witnessBlock4 v
        else
          if v.val < 384 then
            witnessBlock5 v
          else
            witnessBlock6 v
    else
      if v.val < 704 then
        if v.val < 576 then
          if v.val < 512 then
            witnessBlock7 v
          else
            witnessBlock8 v
        else
          if v.val < 640 then
            witnessBlock9 v
          else
            witnessBlock10 v
      else
        if v.val < 832 then
          if v.val < 768 then
            witnessBlock11 v
          else
            witnessBlock12 v
        else
          if v.val < 896 then
            witnessBlock13 v
          else
            witnessBlock14 v
  else
    if v.val < 1408 then
      if v.val < 1152 then
        if v.val < 1024 then
          witnessBlock15 v
        else
          if v.val < 1088 then
            witnessBlock16 v
          else
            witnessBlock17 v
      else
        if v.val < 1280 then
          if v.val < 1216 then
            witnessBlock18 v
          else
            witnessBlock19 v
        else
          if v.val < 1344 then
            witnessBlock20 v
          else
            witnessBlock21 v
    else
      if v.val < 1664 then
        if v.val < 1536 then
          if v.val < 1472 then
            witnessBlock22 v
          else
            witnessBlock23 v
        else
          if v.val < 1600 then
            witnessBlock24 v
          else
            witnessBlock25 v
      else
        if v.val < 1792 then
          if v.val < 1728 then
            witnessBlock26 v
          else
            witnessBlock27 v
        else
          if v.val < 1856 then
            witnessBlock28 v
          else
            witnessBlock29 v⟩
theorem accepted : fastCheck graph root certificate = true := by
  apply fastCheck_of_parts
  · timed_kernel_decide
  ·
    apply all_range'_split 0 932 932
    ·
      apply all_range'_split 0 466 466
      ·
        apply all_range'_split 0 233 233
        ·
          apply all_range'_split 0 116 117
          ·
            apply all_range'_split 0 58 58
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
          ·
            apply all_range'_split 116 58 59
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
        ·
          apply all_range'_split 233 116 117
          ·
            apply all_range'_split 233 58 58
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
          ·
            apply all_range'_split 349 58 59
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
      ·
        apply all_range'_split 466 233 233
        ·
          apply all_range'_split 466 116 117
          ·
            apply all_range'_split 466 58 58
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
          ·
            apply all_range'_split 582 58 59
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
        ·
          apply all_range'_split 699 116 117
          ·
            apply all_range'_split 699 58 58
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
          ·
            apply all_range'_split 815 58 59
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
    ·
      apply all_range'_split 932 466 466
      ·
        apply all_range'_split 932 233 233
        ·
          apply all_range'_split 932 116 117
          ·
            apply all_range'_split 932 58 58
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
          ·
            apply all_range'_split 1048 58 59
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
        ·
          apply all_range'_split 1165 116 117
          ·
            apply all_range'_split 1165 58 58
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
          ·
            apply all_range'_split 1281 58 59
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
      ·
        apply all_range'_split 1398 233 233
        ·
          apply all_range'_split 1398 116 117
          ·
            apply all_range'_split 1398 58 58
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
          ·
            apply all_range'_split 1514 58 59
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
        ·
          apply all_range'_split 1631 116 117
          ·
            apply all_range'_split 1631 58 58
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
          ·
            apply all_range'_split 1747 58 59
            ·
              timed_kernel_decide
            ·
              timed_kernel_decide
  · change ([edgeBlock0, edgeBlock1, edgeBlock2, edgeBlock3, edgeBlock4, edgeBlock5, edgeBlock6, edgeBlock7, edgeBlock8, edgeBlock9, edgeBlock10, edgeBlock11, edgeBlock12, edgeBlock13, edgeBlock14, edgeBlock15, edgeBlock16, edgeBlock17, edgeBlock18, edgeBlock19, edgeBlock20, edgeBlock21, edgeBlock22, edgeBlock23, edgeBlock24, edgeBlock25, edgeBlock26, edgeBlock27, edgeBlock28, edgeBlock29, edgeBlock30, edgeBlock31, edgeBlock32, edgeBlock33, edgeBlock34, edgeBlock35, edgeBlock36, edgeBlock37, edgeBlock38, edgeBlock39, edgeBlock40, edgeBlock41, edgeBlock42, edgeBlock43, edgeBlock44, edgeBlock45, edgeBlock46, edgeBlock47, edgeBlock48, edgeBlock49, edgeBlock50, edgeBlock51, edgeBlock52, edgeBlock53, edgeBlock54, edgeBlock55, edgeBlock56, edgeBlock57, edgeBlock58, edgeBlock59, edgeBlock60, edgeBlock61, edgeBlock62, edgeBlock63, edgeBlock64, edgeBlock65, edgeBlock66, edgeBlock67, edgeBlock68, edgeBlock69]).all (fun b => b.all (fastClosure certificate)) = true
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    apply all_cons_true
    · timed_kernel_decide
    rfl
theorem erased_accepted : check (eraseGraph graph) root (eraseHints certificate) = true :=
  fastCheck_refines graph root certificate accepted
theorem exact (v : Fin 1864) :
    fastMember certificate v = true ↔
      Reach (ReverseEdge (fun a b => (a,b) ∈ (eraseGraph graph).edges)) root v :=
  fastCheck_exact graph root certificate accepted v
end ChromiumFast
#print axioms ChromiumFast.accepted
#print axioms ChromiumFast.erased_accepted
#print axioms ChromiumFast.exact
