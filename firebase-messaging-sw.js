// Firebase Messaging Service Worker
// This file must be at the root of your domain (scope: /)

importScripts('https://www.gstatic.com/firebasejs/12.10.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/12.10.0/firebase-messaging-compat.js');

// Firebase configuration will be injected by Django view (home/views.py firebase_messaging_sw)
// The view reads FIREBASE_CONFIG from settings and embeds it here as: const firebaseConfig = {...};
// If not injected, use empty object as fallback
const firebaseConfig = typeof firebaseConfig !== 'undefined' ? firebaseConfig : {};

// Only initialize if config is present
if (firebaseConfig.apiKey) {
    firebase.initializeApp(firebaseConfig);
    
    // Get the Messaging instance
    const messaging = firebase.messaging();
    
    // Handle background messages
    messaging.onBackgroundMessage((payload) => {
        console.log('FCM background message:', payload);
        
        const notificationTitle = payload.notification?.title || 'Chat Message';
        const notificationOptions = {
            body: payload.notification?.body || '',
            icon: payload.notification?.icon || '/favicon.ico',
            badge: payload.notification?.badge || '/favicon.ico',
            data: payload.data || {},
            requireInteraction: true
        };

        self.registration.showNotification(notificationTitle, notificationOptions);
    });
} else {
    console.warn('Firebase configuration not available. Push notifications disabled.');
}

// Handle notification click
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    
    const clickAction = event.notification.data?.click_action;
    if (clickAction) {
        event.waitUntil(
            clients.openWindow(clickAction)
        );
    }
});
