export function hexToRgba(hex: string, opacity: number) {
    const r = parseInt(hex.slice(1, 3), 16),
        g = parseInt(hex.slice(3, 5), 16),
        b = parseInt(hex.slice(5, 7), 16);

    if (opacity) {
        return "rgba(" + r + ", " + g + ", " + b + ", " + opacity + ")";
    } else {
        return "rgb(" + r + ", " + g + ", " + b + ")";
    }
}