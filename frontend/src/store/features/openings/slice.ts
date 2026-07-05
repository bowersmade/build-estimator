import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import type { OpeningsState, Opening } from './types'

const initialState: OpeningsState = {
  items: [],
  selectedWallId: null,
}

const openingsSlice = createSlice({
  name: 'openings',
  initialState,
  reducers: {
    addOpening: (state, action: PayloadAction<Opening>) => {
      state.items.push(action.payload)
    },
    removeOpening: (state, action: PayloadAction<number>) => {
      state.items.splice(action.payload, 1)
    },
    setSelectedWallId: (state, action: PayloadAction<string | null>) => {
      state.selectedWallId = action.payload
    },
  },
})

export const { addOpening, removeOpening, setSelectedWallId } = openingsSlice.actions
export default openingsSlice.reducer
