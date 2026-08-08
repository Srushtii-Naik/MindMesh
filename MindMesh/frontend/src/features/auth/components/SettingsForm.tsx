import { useSettings, useUpdateSettings } from '@/features/auth/hooks';
import { useUIStore } from '@/stores/uiStore';
import type { ThemePreference } from '@/features/auth/types';

const THEME_OPTIONS: { value: ThemePreference; label: string }[] = [
  { value: 'system', label: 'Match system' },
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
];

export function SettingsForm() {
  const { data: settings, isLoading, isError } = useSettings();
  const updateSettings = useUpdateSettings();
  const setTheme = useUIStore((state) => state.setTheme);

  if (isLoading) {
    return <p className="text-sm text-slate-500 dark:text-slate-400">Loading settings…</p>;
  }

  if (isError || !settings) {
    return (
      <p className="text-sm text-red-600 dark:text-red-400">Couldn&apos;t load your settings.</p>
    );
  }

  const handleThemeChange = (theme_preference: ThemePreference) => {
    updateSettings.mutate({ theme_preference });
    // Reflect the choice immediately in the existing UI store so the app's
    // own light/dark styling (Tailwind's `dark` class) responds right away,
    // without waiting on the settings query to refetch.
    if (theme_preference !== 'system') {
      setTheme(theme_preference);
    }
  };

  const handleNotificationsToggle = (checked: boolean) => {
    updateSettings.mutate({ email_notifications_enabled: checked });
  };

  return (
    <div className="space-y-6">
      <div>
        <span className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">
          Theme
        </span>
        <div className="flex gap-2">
          {THEME_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleThemeChange(option.value)}
              aria-pressed={settings.theme_preference === option.value}
              className={`rounded-md border px-3 py-1.5 text-sm transition ${
                settings.theme_preference === option.value
                  ? 'border-brand-600 bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-300'
                  : 'border-slate-300 text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <span className="block text-sm font-medium text-slate-700 dark:text-slate-300">
            Email notifications
          </span>
          <p className="text-xs text-slate-400">Receive email updates from MindMesh.</p>
        </div>
        <button
          type="button"
          role="switch"
          aria-checked={settings.email_notifications_enabled}
          onClick={() => handleNotificationsToggle(!settings.email_notifications_enabled)}
          className={`relative h-6 w-11 rounded-full transition ${
            settings.email_notifications_enabled ? 'bg-brand-600' : 'bg-slate-300 dark:bg-slate-700'
          }`}
        >
          <span
            className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition ${
              settings.email_notifications_enabled ? 'left-5' : 'left-0.5'
            }`}
          />
        </button>
      </div>
    </div>
  );
}
