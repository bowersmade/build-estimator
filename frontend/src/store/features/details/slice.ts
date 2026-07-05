import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import type { DetailsState, Roofing } from './types'

const initialState: DetailsState = {
  roofing: { type: 'gable', pitch: 6, material: 'architectural_shingles' },
}

const detailsSlice = createSlice({
  name: 'details',
  initialState,
  reducers: {
    setRoofing: (state, action: PayloadAction<Roofing>) => {
      state.roofing = action.payload
    },
  },
})

export const { setRoofing } = detailsSlice.actions
export default detailsSlice.reducer
