export type RoofType = 'gable' | 'hip' | 'flat' | 'shed'

export interface Roofing {
  type: RoofType
  pitch: number
  material: string
}

export interface DetailsState {
  roofing: Roofing
}
