import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import type { FoundationState, Room } from './types'

const initialState: FoundationState = {
  rooms: [],
}

const foundationSlice = createSlice({
  name: 'foundation',
  initialState,
  reducers: {
    addRoom: (state, action: PayloadAction<Room>) => {
      state.rooms.push(action.payload)
    },
    removeRoom: (state, action: PayloadAction<number>) => {
      state.rooms.splice(action.payload, 1)
    },
  },
})

export const { addRoom, removeRoom } = foundationSlice.actions
export default foundationSlice.reducer
