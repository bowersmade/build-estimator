import type { RootState } from '../../store'

const GRID = 10

export const selectRooms = (state: RootState) => state.foundation.rooms

export const selectTotalSqft = (state: RootState): number =>
  state.foundation.rooms.reduce((sum, r) => {
    const wFt = Math.abs(r.x2 - r.x1) / GRID
    const hFt = Math.abs(r.y2 - r.y1) / GRID
    return sum + wFt * hFt
  }, 0)
