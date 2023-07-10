import React from 'react';
import MarkdownView, { MarkdownViewProps } from 'react-showdown';

export const markdownOptions: MarkdownViewProps['options'] = {
    simpleLineBreaks: true,
    headerLevelStart: 3,
    simplifiedAutoLink: true,
    openLinksInNewWindow: true,
    backslashEscapesHTMLTags: true,
    literalMidWordUnderscores: true,
    strikethrough: true,
    tables: true,
    tasklists: true,
};

export default function MarkdownPreview(props: MarkdownViewProps) {
    const {
        options: markdownOptionsFromProps,
        ...otherProps
    } = props;
    return (
        <MarkdownView
            {...otherProps}
            options={markdownOptionsFromProps ?? markdownOptions}
        />
    );
}
