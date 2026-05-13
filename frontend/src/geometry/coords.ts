export type WorldPoint = {
    readonly x: number;
    readonly y: number;
    readonly _kind: 'world';
}

export type ScreenPoint = {
    readonly x: number;
    readonly y: number;
    readonly _kind: 'screen';
}

export function world(x: number, y: number): WorldPoint {
    return {x, y} as WorldPoint
}

export function screen(x: number, y: number): ScreenPoint {
    return {x, y} as ScreenPoint
}