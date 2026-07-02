/**
 * Fetches the authenticated user's subscription plan from the backend.
 * Returns plan_id ('free', 'single', 'family', 'business') and feature list.
 */
import { apiRequest } from './http'
import { getAuthHeaders, isAuthenticated } from './auth'

export type PlanInfo = {
  plan_id: 'free' | 'single' | 'family' | 'business'
  features: string[]
}

export async function fetchUserPlan(): Promise<PlanInfo | null> {
  if (!isAuthenticated()) return null
  try {
    return await apiRequest<PlanInfo>('/api/account/plan', { headers: getAuthHeaders() })
  } catch {
    return null
  }
}

export function planLabel(planId: string): string {
  const labels: Record<string, string> = {
    free: 'Free',
    single: 'Single',
    family: 'Family',
    business: 'Business',
  }
  return labels[planId] ?? planId
}
