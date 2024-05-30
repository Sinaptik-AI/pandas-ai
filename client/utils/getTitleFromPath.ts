export const getTitleFromPath = (pathname: string) => {
    if (pathname.includes("chat")) return "Chat";
    if (pathname.includes("datasets")) return "Datasets";
    if (pathname.includes("workspace")) return "Workspace";
    if (pathname.includes("test")) return "Test";
    if (pathname.includes("logs")) return "Logs";
    if (pathname.includes("spaces")) return "Spaces";
    if (pathname.includes("api-keys")) return "Api Keys";
    if (pathname.includes("organization")) return "Organization";
    if (pathname.includes("sign-up")) return "Sign-up";
    if (pathname.includes("conversation")) return "Conversation";
    if (pathname.includes("train")) return "Train";
    if (pathname.includes("feed")) return "Feed";
    if (pathname.includes("admin")) return "Admin";
    return "Sign In";
};
