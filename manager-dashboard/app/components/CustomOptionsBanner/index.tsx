import React from 'react';
import {IoAlertCircleOutline} from 'react-icons/io5';
import styles from './styles.css';

function CustomOptionsBanner() {
    return (
        <div className={styles.banner}>
            <div>
                <IoAlertCircleOutline />
            </div>
            <div>
                While creating options, please use the values as listed below for HOT Tasking Manager Geometries
            </div>
        </div>
    );
}

export default CustomOptionsBanner;