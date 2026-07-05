import type { EstimateResult } from '../store/features/estimate/types'

export async function postEstimate(payload: Record<string, unknown>): Promise<EstimateResult> {
  const res = await fetch('/estimate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const err = await res.json()
    throw new Error(typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail))
  }

  return res.json() as Promise<EstimateResult>
}
