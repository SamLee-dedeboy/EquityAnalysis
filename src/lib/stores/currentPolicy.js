// src/lib/stores/currentPolicy.js
import { writable } from 'svelte/store';
import { server_address } from '../../constants.ts';

export const currentPolicy = writable(null);

export async function fetchPolicies() {
    return fetch(`${server_address}/api/policies`)
      .then((response) => response.json())
      .then((data) => {
        console.log("Fetched policies:", data);
        return data
      })
      .catch((error) => {
        console.error("Error fetching policies:", error);
      });
  }

export function fetchPolicyDataById(policyId) {
    return fetch(`${server_address}/api/policies/${policyId}`)
    .then((response) => response.json())
    .then((data) => {
        return data;
    })
}