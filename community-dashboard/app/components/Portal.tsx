import React from 'react';
import ReactDOM from 'react-dom';

export interface PortalProps {
    children: React.ReactNode;
}

function Portal(props: PortalProps) {
    const { children } = props;
    return (
        <>
            {ReactDOM.createPortal(
                children,
                document.body,
            )}
        </>
    );
}

export default Portal;
