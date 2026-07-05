import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { addRoom, removeRoom } from '../foundation/slice'
import { addWall, removeWall, setActiveType, setActiveHeight } from '../walls/slice'
import { addOpening, removeOpening } from '../openings/slice'
import { setRoofing } from '../details/slice'
import type { EstimateState, EstimateResult } from './types'

const invalidatingActions = [
  addRoom, removeRoom,
  addWall, removeWall, setActiveType, setActiveHeight,
  addOpening, removeOpening,
  setRoofing,
]

const initialState: EstimateState = {
  result: null,
  error: null,
  loading: false,
}

const estimateSlice = createSlice({
  name: 'estimate',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
    setResult: (state, action: PayloadAction<EstimateResult>) => {
      state.result = action.payload
      state.error = null
      state.loading = false
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload
      state.loading = false
    },
    clearEstimate: (state) => {
      state.result = null
      state.error = null
      state.loading = false
    },
  },
  extraReducers: (builder) => {
    invalidatingActions.forEach((action) => {
      builder.addCase(action, (state) => {
        state.result = null
        state.error = null
      })
    })
  },
})

export const { setLoading, setResult, setError, clearEstimate } = estimateSlice.actions
export default estimateSlice.reducer
