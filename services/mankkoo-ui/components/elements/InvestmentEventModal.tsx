"use client";

import { useState, SyntheticEvent } from "react";
import axios from "axios";
import withReactContent from "sweetalert2-react-content";
import Swal from "sweetalert2";

import Modal from "./Modal";
import classes from "./InvestmentEventModal.module.css";
import { API_BASE } from "@/api/ApiUrl";
import { 
  InvestmentStreamResponse, 
  CreateInvestmentEventRequest, 
  CreateInvestmentEventResponse 
} from "@/api/InvestmentsPageResponses";

const MySwal = withReactContent(Swal);

interface InvestmentEventModalProps {
  isOpen: boolean;
  onClose: () => void;
  streams: InvestmentStreamResponse[];
  onEventCreated: () => void;
}

export default function InvestmentEventModal({
  isOpen,
  onClose,
  streams,
  onEventCreated
}: InvestmentEventModalProps) {
  // State management
  const [selectedStreamId, setSelectedStreamId] = useState("");
  const [eventType, setEventType] = useState<"buy" | "sell" | "price_update">("buy");
  const [occuredAt, setOccuredAt] = useState(new Date().toISOString().split('T')[0]);
  const [units, setUnits] = useState("");
  const [totalValue, setTotalValue] = useState("");
  const [pricePerUnit, setPricePerUnit] = useState("");
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // Validation function
  const validateForm = (): boolean => {
    if (!selectedStreamId) {
      setErrorMessage("Please select an investment stream");
      return false;
    }
    if (!occuredAt) {
      setErrorMessage("Please select a date");
      return false;
    }
    if (eventType === "price_update") {
      const price = parseFloat(pricePerUnit);
      if (!pricePerUnit || isNaN(price) || price <= 0) {
        setErrorMessage("Price per unit must be greater than 0");
        return false;
      }
    } else {
      const unitsNum = parseFloat(units);
      const totalNum = parseFloat(totalValue);
      if (!units || isNaN(unitsNum) || unitsNum <= 0) {
        setErrorMessage("Units must be greater than 0");
        return false;
      }
      if (!totalValue || isNaN(totalNum) || totalNum <= 0) {
        setErrorMessage("Total value must be greater than 0");
        return false;
      }
    }
    return true;
  };

  // Reset form
  const resetForm = () => {
    setSelectedStreamId("");
    setEventType("buy");
    setOccuredAt(new Date().toISOString().split('T')[0]);
    setUnits("");
    setTotalValue("");
    setPricePerUnit("");
    setComment("");
    setErrorMessage("");
    setIsSubmitting(false);
  };

  // Submit handler
  const handleSubmit = async (event: SyntheticEvent) => {
    event.preventDefault();
    setErrorMessage("");

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    const requestBody: CreateInvestmentEventRequest = {
      streamId: selectedStreamId,
      eventType: eventType,
      occuredAt: occuredAt,
      units: eventType !== "price_update" ? parseFloat(units) : undefined,
      totalValue: eventType !== "price_update" ? parseFloat(totalValue) : undefined,
      pricePerUnit: eventType === "price_update" ? parseFloat(pricePerUnit) : undefined,
      comment: comment.trim() || undefined
    };

    try {
      const response = await axios.post<CreateInvestmentEventResponse>(
        `${API_BASE}/investments/events`,
        requestBody,
        { headers: { "Content-Type": "application/json" } }
      );

      if (response.data.result === "Success") {
        MySwal.fire({
          title: "Success!",
          text: "Investment event created successfully",
          icon: "success",
          confirmButtonText: "Cool"
        });
        resetForm();
        onEventCreated();
        onClose();
      } else {
        setErrorMessage(response.data.details || "Failed to create event");
        setIsSubmitting(false);
      }
    } catch (error) {
      let errorMsg = "Failed to create investment event";
      if (axios.isAxiosError(error) && error.response?.data?.details) {
        errorMsg = error.response.data.details;
      }
      setErrorMessage(errorMsg);
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      header="Add Investment Transaction"
      subHeader="Create a new buy, sell, or price update event"
      onSubmit={handleSubmit}
      onClose={handleClose}
    >
      <form className={classes.form}>
        {errorMessage && (
          <div className={classes.errorMessage}>❌ {errorMessage}</div>
        )}

        <div className={classes.formGroup}>
          <label htmlFor="stream">Investment Stream</label>
          <select
            id="stream"
            value={selectedStreamId}
            onChange={(e) => setSelectedStreamId(e.target.value)}
            disabled={isSubmitting}
            className={classes.select}
          >
            <option value="">-- Select Investment --</option>
            {streams.map((stream) => (
              <option key={stream.id} value={stream.id}>
                {stream.name} ({stream.subtype})
              </option>
            ))}
          </select>
        </div>

        <div className={classes.formGroup}>
          <label htmlFor="eventType">Event Type</label>
          <select
            id="eventType"
            value={eventType}
            onChange={(e) => setEventType(e.target.value as "buy" | "sell" | "price_update")}
            disabled={isSubmitting}
            className={classes.select}
          >
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
            <option value="price_update">Price Update</option>
          </select>
        </div>

        <div className={classes.formGroup}>
          <label htmlFor="occuredAt">Date of Occurrence</label>
          <input
            type="date"
            id="occuredAt"
            value={occuredAt}
            onChange={(e) => setOccuredAt(e.target.value)}
            disabled={isSubmitting}
            className={classes.input}
          />
        </div>

        {eventType !== "price_update" && (
          <>
            <div className={classes.formGroup}>
              <label htmlFor="units">Units</label>
              <input
                type="number"
                id="units"
                value={units}
                onChange={(e) => setUnits(e.target.value)}
                disabled={isSubmitting}
                placeholder="0"
                step="0.01"
                min="0"
                className={classes.input}
              />
            </div>

            <div className={classes.formGroup}>
              <label htmlFor="totalValue">Total Price (PLN)</label>
              <input
                type="number"
                id="totalValue"
                value={totalValue}
                onChange={(e) => setTotalValue(e.target.value)}
                disabled={isSubmitting}
                placeholder="0.00"
                step="0.01"
                min="0"
                className={classes.input}
              />
            </div>
          </>
        )}

        {eventType === "price_update" && (
          <div className={classes.formGroup}>
            <label htmlFor="pricePerUnit">Price Per Unit (PLN)</label>
            <input
              type="number"
              id="pricePerUnit"
              value={pricePerUnit}
              onChange={(e) => setPricePerUnit(e.target.value)}
              disabled={isSubmitting}
              placeholder="0.00"
              step="0.01"
              min="0"
              className={classes.input}
            />
          </div>
        )}

        <div className={classes.formGroup}>
          <label htmlFor="comment">Comment (optional)</label>
          <textarea
            id="comment"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            disabled={isSubmitting}
            maxLength={500}
            rows={3}
            className={classes.textarea}
            placeholder="Add any notes..."
          />
        </div>
      </form>
    </Modal>
  );
}
