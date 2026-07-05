import { configureStore } from '@reduxjs/toolkit'
import foundationReducer from './features/foundation/slice'
import wallsReducer from './features/walls/slice'
import openingsReducer from './features/openings/slice'
import detailsReducer from './features/details/slice'
import estimateReducer from './features/estimate/slice'
import uiReducer from './features/ui/slice'

export const store = configureStore({
  reducer: {
    foundation: foundationReducer,
    walls: wallsReducer,
    openings: openingsReducer,
    details: detailsReducer,
    estimate: estimateReducer,
    ui: uiReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
