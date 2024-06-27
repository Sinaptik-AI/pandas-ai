export const isBase64Image = (str) => {
  if (typeof str === "string" && str?.startsWith("data:image/")) {
    const base64Regex = /^data:image\/\w+;base64,/;
    return base64Regex?.test(str);
  }
  return false;
};
