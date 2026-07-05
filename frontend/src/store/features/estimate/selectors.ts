import type { RootState } from '../../store'

export const selectEstimateResult = (state: RootState) => state.estimate.result
export const selectEstimateError = (state: RootState) => state.estimate.error
export const selectEstimateLoading = (state: RootState) => state.estimate.loading
