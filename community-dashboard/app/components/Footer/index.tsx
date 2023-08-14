import React from 'react';
import { IoLogoTwitter, IoLogoGithub, IoMail } from 'react-icons/io5';
import iosSvg from '#resources/icons/ios.svg';
import androidSvg from '#resources/icons/android.svg';

import styles from './styles.css';

function Footer() {
    return (
        <div className={styles.footer}>
            <div className={styles.links}>
                <a
                    aria-label="Ios"
                    href="https://itunes.apple.com/us/app/mapswipe/id1133855392?ls=1&mt=8"
                    rel="noreferrer"
                    target="_blank"
                >
                    <img src={iosSvg} alt="ios download icon" className={styles.image} />
                </a>
                <a
                    aria-label="Android"
                    target="_blank"
                    rel="noreferrer"
                    href="https://play.google.com/store/apps/details?id=org.missingmaps.mapswipe"
                >
                    <img src={androidSvg} alt="android download icon" className={styles.image} />
                </a>
            </div>
            <div className={styles.links}>
                <a
                    aria-label="Twitter"
                    href="https://twitter.com/mapswipe"
                    target="_blank"
                    className={styles.iconLink}
                    rel="noreferrer"
                >
                    <IoLogoTwitter />
                </a>
                <a
                    aria-label="Github"
                    href="https://github.com/mapswipe"
                    target="_blank"
                    rel="noreferrer"
                    className={styles.iconLink}
                >
                    <IoLogoGithub />
                </a>
                <a
                    aria-label="Email"
                    href="mailto:info@mapswipe.org"
                    target="_blank"
                    rel="noreferrer"
                    className={styles.iconLink}
                >
                    <IoMail />
                </a>
            </div>
            <div className={styles.links}>
                <a
                    aria-label="Privacy"
                    href="https://mapswipe.org/en/privacy"
                    target="_blank"
                    rel="noreferrer"
                    className={styles.link}
                >
                    Privacy
                </a>
                <span
                    className={styles.link}
                >
                    Copyright © 2022 MapSwipe
                </span>
            </div>
        </div>
    );
}

export default Footer;
