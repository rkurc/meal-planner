// frontend/src/App.jsx
import React from 'react';
import RecipeList from './components/RecipeList'; // Import RecipeList

function App() {
  return (
    // Minimal wrapper, or can include global layout elements here later
    <div>
      <RecipeList />
    </div>
  );
}

export default App;
