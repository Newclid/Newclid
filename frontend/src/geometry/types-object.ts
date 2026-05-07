export type ObjectId = string;

export interface PointObject {
    id: ObjectId;
    kind: 'point'
    x: number;
    y: number;
    label: string;

}

