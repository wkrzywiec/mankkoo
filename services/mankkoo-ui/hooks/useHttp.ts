import { useEffect, useState } from 'react';
import axios from 'axios';
import { API_BASE } from '@/api/ApiUrl';

export function useGetHttp<Type>(apiPath: string): {isFetching?: boolean, fetchedData?: Type, setFetchedData?: unknown, error?: string } {
  
    const [isFetching, setIsFetching] = useState<boolean>();
    const [error, setError] = useState<string>();
    const [fetchedData, setFetchedData] = useState<Type>();

    useEffect(() => {
        async function fetchData() {
        setIsFetching(true);
        try {
            const response = await axios.get<Type>(API_BASE + apiPath);
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
    }, [apiPath]);

    return {
        isFetching,
        fetchedData,
        setFetchedData,
        error
    }
}

