import Headline from "@/components/elements/Headline"
import SubHeadline from "@/components/elements/SubHeadline"
import { ReactNode } from 'react';

export default function TileHeader({headline, children}: {headline: string, children: ReactNode}) {
    return (
        <>
            <Headline text={headline} fontSize="2" />
            <SubHeadline>
                {children}
            </SubHeadline>
        </>
    )
}