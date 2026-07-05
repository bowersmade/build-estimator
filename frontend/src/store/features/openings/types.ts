export type OpeningType = 'window' | 'door'

export interface Opening {
  wallId: string
  type: OpeningType
  width: number
  height: number
  position: number
}

export interface OpeningsState {
  items: Opening[]
  selectedWallId: string | null
}
