export interface EstimateResult {
  total_cost: number
  cost_per_sqft: number
  materials: number
  permits: number
  cost_breakdown: Record<string, number>
  warnings: string[]
  selections: Record<string, string[]>
}

export interface EstimateState {
  result: EstimateResult | null
  error: string | null
  loading: boolean
}

export interface RoofingCatalogItem {
  key: string
  display_name: string
  price_per_sqft: number
  flat_only: boolean
}
