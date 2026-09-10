import { useEffect, useState } from "react";
import { api } from "../api.js";

export function useCatalogLookups() {
  const [knownIngredients, setKnownIngredients] = useState([]);
  const [knownLocations, setKnownLocations] = useState([]);
  const [knownUnits, setKnownUnits] = useState([]);
  const [ingredientDefaultUnits, setIngredientDefaultUnits] = useState({});

  useEffect(() => {
    api
      .get("/api/ingredients/summary")
      .then((data) => {
        if (!Array.isArray(data)) {
          return;
        }
        const names = [];
        const map = {};
        data.forEach((item) => {
          if (item && item.name) {
            names.push(item.name);
            map[item.name] = item.unit || "";
          }
        });
        setKnownIngredients(names);
        setIngredientDefaultUnits(map);
      })
      .catch(() => {
        // non-fatal for suggestions
      });

    api
      .get("/api/locations")
      .then((data) => {
        if (Array.isArray(data)) {
          setKnownLocations(data);
        }
      })
      .catch(() => {
        // non-fatal
      });

    api
      .get("/api/units")
      .then((data) => {
        if (Array.isArray(data)) {
          setKnownUnits(data);
        }
      })
      .catch(() => {
        // non-fatal
      });
  }, []);

  return {
    knownIngredients,
    knownLocations,
    knownUnits,
    ingredientDefaultUnits,
  };
}
