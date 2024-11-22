import Headline from "@/components/elements/Headline"
import SubHeadline from "@/components/elements/SubHeadline"
import { ReactNode } from 'react';

export default function TileHeader({headline, subHeadline, headlineElement}: {headline?: string, subHeadline?: string | ReactNode, headlineElement?: ReactNode}) {
    return (
        <>
            <Headline text={headline} fontSize="2">{headlineElement}</Headline>
            <SubHeadline text={subHeadline} />
        </>
    )
}