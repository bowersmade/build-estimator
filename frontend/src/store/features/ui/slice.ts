import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface UiState {
  currentStep: number
}

const initialState: UiState = {
  currentStep: 1,
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setCurrentStep: (state, action: PayloadAction<number>) => {
      state.currentStep = action.payload
    },
  },
})

export const { setCurrentStep } = uiSlice.actions
export default uiSlice.reducer
