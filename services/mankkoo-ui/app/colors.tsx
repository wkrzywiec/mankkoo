export enum Colors {
    Red = "#ED6B53",
    Black = "#463F3A",
    Blue = "#6883BA",
    Gold = "#CBA328",
    Green = "#6E9075",
    Pink = "#EC9192",
    Blueberry = "#B68CB8",
    Orange = "#FFA630",
}

export const mankkooColors = Object.values(Colors);

// todo: make sure that index can be bigger 
export function getColor(index: number) {
    return mankkooColors[index]
}
