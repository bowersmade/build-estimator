import type { RootState } from '../../store'

export const selectWalls = (state: RootState) => state.walls.segments
export const selectActiveWallType = (state: RootState) => state.walls.activeType
export const selectActiveWallHeight = (state: RootState) => state.walls.activeHeight
