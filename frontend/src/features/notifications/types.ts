export type NotificationType = 'reminder' | 'system';

export type NotificationChannel = 'in_app' | 'email' | 'push';

export type DeliveryStatus = 'pending' | 'sent' | 'failed';

export type DevicePlatform = 'web' | 'ios' | 'android';

export interface LinkedReminder {
  id: string;
  title: string;
}

export interface NotificationDelivery {
  id: string;
  channel: NotificationChannel;
  status: DeliveryStatus;
  error_message: string;
  sent_at: string | null;
  created_at: string;
}

export interface Notification {
  id: string;
  notification_type: NotificationType;
  title: string;
  message: string;
  reminder: LinkedReminder | null;
  is_read: boolean;
  read_at: string | null;
  deliveries: NotificationDelivery[];
  created_at: string;
  updated_at: string;
}

export interface NotificationFilters {
  is_read?: boolean;
  notification_type?: NotificationType;
}

export interface DeviceToken {
  id: string;
  token: string;
  platform: DevicePlatform;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DeviceTokenPayload {
  token: string;
  platform?: DevicePlatform;
}
