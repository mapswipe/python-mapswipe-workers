import React from 'react';
import ReactDom from 'react-dom';
import Base from './Base';

// NOTE: let's enable strict mode
ReactDom.render(
    <Base />,
    document.getElementById('app-container'),
);
