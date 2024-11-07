import axios from 'axios';
import MainIndicatorsResponse from './MainIndicatorsResponse';

export const fetchIndicators = async (): Promise<MainIndicatorsResponse> => {
  const response = await axios.get<MainIndicatorsResponse>('http://localhost:5000/api/main/indicators');
  return response.data;
};