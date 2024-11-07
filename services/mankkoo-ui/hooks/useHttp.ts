import { useEffect, useState } from 'react';
import axios from 'axios';

export function useGetHttp<Type>(url: string): {isFetching?: boolean, fetchedData?: Type, setFetchedData?: unknown, error?: string } {
  
    const [isFetching, setIsFetching] = useState<boolean>();
    const [error, setError] = useState<string>();
    const [fetchedData, setFetchedData] = useState<Type>();

    useEffect(() => {
        async function fetchData() {
        setIsFetching(true);
        try {
            const response = await axios.get<Type>(url);
            setFetchedData(response.data);
        } catch (error) {
            let errorMessage = 'Failed to fetch data from ';
            
            if (error instanceof Error) {
                errorMessage = error.message
            } 
            setError(errorMessage);
        }

        setIsFetching(false);
        }

        fetchData();
    }, [url]);

    return {
        isFetching,
        fetchedData,
        setFetchedData,
        error
    }
}

