export type WallType = 'exterior' | 'interior_finished' | 'interior_unfinished'

export interface Wall {
  id: string
  x1: number
  y1: number
  x2: number
  y2: number
  type: WallType
  height: number
}

export interface WallsState {
  segments: Wall[]
  activeType: WallType
  activeHeight: number
}
