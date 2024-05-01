import React, { useEffect, useState } from 'react';
import { db } from './firebase';
import { doc, getDoc } from "firebase/firestore";
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import './App.css';

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lines, setLines] = useState({
    forward1: [],
    forward2: [],
    forward3: [],
    defense1: [],
    defense2: [],
    goalie: []
});

useEffect(() => {
const fetchData = async () => {
  const rsvpRef = doc(db, `voodoo_lovechild_baierl_e1_spring_2024/games/04-28-2024/RSVPs`);
  const docSnap = await getDoc(rsvpRef);

  if (docSnap.exists()) {
    const { attendees, maybes, nos } = docSnap.data();
    const attendeesData = attendees.map((attendee, index) => ({ id: `attendee-${index}`, name: attendee, type: 'attendee' }));
    const maybesData = maybes.map((maybe, index) => ({ id: `maybe-${index}`, name: maybe, type: 'maybe' }));
    const nosData = nos.map((no, index) => ({ id: `no-${index}`, name: no, type: 'no' }));
    setData([...attendeesData, ...maybesData, ...nosData]);
  } else {
    console.log("No such document!");
  }

  setLoading(false);
};

    fetchData();
  }, []);

  const handleDragEnd = (result) => {
    const { source, destination } = result;
  
    // Ignore drops outside of any droppable area
    if (!destination) return;
  
    if (source.droppableId === destination.droppableId) {
      // Reordering within the same list
      const items = Array.from(lines[source.droppableId]);
      const [reorderedItem] = items.splice(source.index, 1);
      items.splice(destination.index, 0, reorderedItem);
  
      setLines({
        ...lines,
        [source.droppableId]: items,
      });
    } else {
      // Moving between lists
      const sourceItems = source.droppableId === 'players' ? Array.from(data) : Array.from(lines[source.droppableId]);
      const destinationItems = Array.from(lines[destination.droppableId]);
      const [movedItem] = sourceItems.splice(source.index, 1);
      destinationItems.splice(destination.index, 0, movedItem);
  
      if (source.droppableId === 'players') {
        setData(sourceItems);
      } else {
        setLines({
          ...lines,
          [source.droppableId]: sourceItems,
        });
      }
  
      setLines({
        ...lines,
        [destination.droppableId]: destinationItems,
      });
    }
  };

  useEffect(() => {
    console.log(lines);
  }, [lines]);

return (
  <div className="App">
    <header className="App-header">
      <h1>Line Builder V3.0</h1>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className='line-builder-container'>
          <DragDropContext onDragEnd={handleDragEnd}>
            <div className='player-pool'>
              <h2>Player Pool</h2>
              <Droppable droppableId="players">
                {(provided) => (
                  <ul className="players" {...provided.droppableProps} ref={provided.innerRef}>
                    {data.map((item, index) => (
                      <Draggable key={item.id} draggableId={item.id} index={index}>
                        {(provided) => (
                          <li ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps} className={item.type}>
                            <p>
                              {item.name}
                            </p>
                          </li>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </ul>
                )}
              </Droppable>
            </div>
            <div className='line-containers-container'>
              {Object.keys(lines).map((lineId) => (
                <div className={`line-container ${lineId}-container`} key={lineId}>
                  <h2>{lineId}</h2>
                  <Droppable droppableId={lineId}>
                    {(provided) => (
                      <ul className={`${lineId}-item on-line`} {...provided.droppableProps} ref={provided.innerRef}>
                        {lines[lineId].map((player, index) => (
                          <Draggable key={player.id} draggableId={player.id} index={index}>
                            {(provided) => (
                              <li ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps} className={`player ${player.type}`}>
                                <p>
                                  {player.name}
                                </p>
                              </li>
                            )}
                          </Draggable>
                        ))}
                        {provided.placeholder}
                      </ul>
                    )}
                  </Droppable>
                </div>
              ))}
            </div>
          </DragDropContext>
        </div>
      )}
    </header>
  </div>
);
}

export default App;

// import React, { useEffect, useState } from 'react';
// import { db } from './firebase';
// import { doc, getDoc } from "firebase/firestore";
// import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
// import './App.css';

// function App() {
//   const [data, setData] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [lines, setLines] = useState({
//     forward1: [],
//     forward2: [],
//     forward3: [],
//     defense1: [],
//     defense2: [],
//     goalie: []
// });

// useEffect(() => {
// const fetchData = async () => {
//   const rsvpRef = doc(db, `voodoo_lovechild_baierl_e1_spring_2024/games/04-28-2024/RSVPs`);
//   const docSnap = await getDoc(rsvpRef);

//   if (docSnap.exists()) {
//     const { attendees, maybes, nos } = docSnap.data();
//     const attendeesData = attendees.map((attendee, index) => ({ id: `attendee-${index}`, name: attendee, type: 'attendee' }));
//     const maybesData = maybes.map((maybe, index) => ({ id: `maybe-${index}`, name: maybe, type: 'maybe' }));
//     const nosData = nos.map((no, index) => ({ id: `no-${index}`, name: no, type: 'no' }));
//     setData([...attendeesData, ...maybesData, ...nosData]);
//   } else {
//     console.log("No such document!");
//   }

//   setLoading(false);
// };

//     fetchData();
//   }, []);

//   const handleDragEnd = (result) => {
//     if (!result.destination) return;

//     const items = Array.from(data);
//     const [reorderedItem] = items.splice(result.source.index, 1);
//     items.splice(result.destination.index, 0, reorderedItem);
//     console.log(items)
//     setData(items);
//   };

//   return (
//     <div className="App">
//       <header className="App-header">
//         <h1>Line Builder V3.0</h1>
//         {loading ? (
//           <p>Loading...</p>
//         ) : (
//           <DragDropContext onDragEnd={handleDragEnd}>
//             <Droppable droppableId="players">
//               {(provided) => (
//                 <ul className="players" {...provided.droppableProps} ref={provided.innerRef}>
//                   {data.map((item, index) => (
//                     <Draggable key={item.id} draggableId={item.id} index={index}>
//                       {(provided) => (
//                         <li ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps} className={item.type}>
//                           <p>
//                             {item.name}
//                           </p>
//                         </li>
//                       )}
//                     </Draggable>
//                   ))}
//                   {provided.placeholder}
//                 </ul>
//               )}
//             </Droppable>
//         </DragDropContext>
//         )}
//       </header>
//     </div>
//   );
// }

// export default App;