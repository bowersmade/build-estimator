import type { RootState } from '../../store'

export const selectOpenings = (state: RootState) => state.openings.items
export const selectSelectedWallId = (state: RootState) => state.openings.selectedWallId
