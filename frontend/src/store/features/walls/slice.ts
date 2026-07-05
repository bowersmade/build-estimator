import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import type { WallsState, Wall, WallType } from './types'

const initialState: WallsState = {
  segments: [],
  activeType: 'exterior',
  activeHeight: 9,
}

const wallsSlice = createSlice({
  name: 'walls',
  initialState,
  reducers: {
    addWall: (state, action: PayloadAction<Wall>) => {
      state.segments.push(action.payload)
    },
    removeWall: (state, action: PayloadAction<number>) => {
      state.segments.splice(action.payload, 1)
    },
    setActiveType: (state, action: PayloadAction<WallType>) => {
      state.activeType = action.payload
    },
    setActiveHeight: (state, action: PayloadAction<number>) => {
      state.activeHeight = action.payload
    },
  },
})

export const { addWall, removeWall, setActiveType, setActiveHeight } = wallsSlice.actions
export default wallsSlice.reducer
