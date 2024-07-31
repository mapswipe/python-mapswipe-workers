// NOTE: We have a similar function in manager-dashbaord
// manager-dashbaord/app/utills/common.tsx

export const formatProjectTopic = (projectTopic: string) => {
    // Note: this will remove start and end space
    const projectWithoutStartAndEndSpace = projectTopic.trim();

    // Note: this will change multi space to single space
    const removeMultiSpaceToSingle = projectWithoutStartAndEndSpace.replace(/\s+/g, ' ');
    const newProjectTopic = removeMultiSpaceToSingle.toLowerCase();

    return newProjectTopic;
};

// NOTE: this validation mirrors feature from the app on signup
export const formatUserName = (name: string) => {
    // Note: remove all space
    const removeUserNameSpace = name.replace(/\s+/g, '');
    const userNameLowercase = removeUserNameSpace.toLowerCase();

    return userNameLowercase;
};
