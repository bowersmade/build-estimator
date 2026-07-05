import type { RootState } from '../../store'
import { selectRooms } from '../foundation/selectors'
import { selectWalls } from '../walls/selectors'
import { selectEstimateResult } from '../estimate/selectors'

export const selectCurrentStep = (state: RootState) => state.ui.currentStep

export const selectCompletedSteps = (state: RootState): number[] => {
  const rooms = selectRooms(state)
  const walls = selectWalls(state)
  const result = selectEstimateResult(state)
  const currentStep = selectCurrentStep(state)

  return ([
    rooms.length > 0 ? 1 : null,
    walls.length > 0 ? 2 : null,
    currentStep > 3 ? 3 : null,
    currentStep > 4 ? 4 : null,
    result ? 5 : null,
  ] as (number | null)[]).filter((s): s is number => s !== null)
}
