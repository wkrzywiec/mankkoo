import Link from 'next/link'
import classes from './menu-item.module.css'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { IconDefinition } from '@fortawesome/fontawesome-common-types'

export default function MenuItem({text, link, icon}: {text: string, link: string, icon: IconDefinition | undefined}) {
    return (
        <li className={classes.menuItem}>
            <Link href={link}>
                <FontAwesomeIcon icon={icon}/>
                <p>{text}</p>
            </Link>
        </li>
    )
}