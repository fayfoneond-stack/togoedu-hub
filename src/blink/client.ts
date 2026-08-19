import { createClient } from '@blinkdotnew/sdk'

export const blink = createClient({
  projectId: import.meta.env.VITE_BLINK_PROJECT_ID || 'togoedu-hub-u6wb5lq7',
  publishableKey: import.meta.env.VITE_BLINK_PUBLISHABLE_KEY || 'blnk_pk_dzI6BIVRcbj5zfKQlM1HlVC17lCSk4Vp',
  authRequired: false,
  auth: { mode: 'managed' },
})
