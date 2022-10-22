import React from 'react';

export interface Props {
    value: string;
}

function PageTitle(props: Props) {
    const { value } = props;
    React.useEffect(
        () => {
            document.title = value;
        },
        [value],
    );
    return null;
}

export default PageTitle;
