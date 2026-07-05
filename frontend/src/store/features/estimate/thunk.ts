import { postEstimate } from '../../../api/estimate'
import { setLoading, setResult, setError } from './slice'
import { selectTotalSqft } from '../foundation/selectors'
import { selectWalls } from '../walls/selectors'
import { selectOpenings } from '../openings/selectors'
import { selectRoofing } from '../details/selectors'
import type { AppDispatch, RootState } from '../../store'

const GRID = 10

function wallLengthFt(wall: { x1: number; y1: number; x2: number; y2: number }): number {
  const dx = wall.x2 - wall.x1
  const dy = wall.y2 - wall.y1
  return Math.max(1, Math.round(Math.sqrt(dx * dx + dy * dy) / GRID))
}

export function fetchEstimate() {
  return async (dispatch: AppDispatch, getState: () => RootState) => {
    const state = getState()
    const totalSqft = selectTotalSqft(state)
    const walls = selectWalls(state)
    const openings = selectOpenings(state)
    const roofing = selectRoofing(state)

    dispatch(setLoading(true))

    const payload: Record<string, unknown> = { square_footage: totalSqft }

    if (walls.length > 0) {
      payload.wall_segments = walls.map((w) => ({
        id: w.id,
        length: wallLengthFt(w),
        height: w.height,
        type: w.type,
        stud_spacing: 16,
        connected_wall_ids: [],
        openings: openings
          .filter((o) => o.wallId === w.id)
          .map((o) => ({ type: o.type, width: o.width, height: o.height, position: o.position })),
      }))
    }

    if (roofing) {
      payload.roof = roofing
    }

    try {
      const data = await postEstimate(payload)
      dispatch(setResult(data))
    } catch (err) {
      dispatch(setError(err instanceof Error ? err.message : 'Unknown error'))
    }
  }
}
