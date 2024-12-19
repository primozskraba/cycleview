import streamlit as st
import numpy as np
import plotly.graph_objects as go
import dionysus as dio
import diode

# Helper function to extract representative cycle
def get_representative_cycle(persistence, filtration,diagram, points, index):
    """Extract representative cycle for the selected persistence point."""
    if not diagram or index >= len(diagram):
        return [],()

    pt = diagram[index]

    x = persistence.pair(pt.data)
    cycle_edges = []
    for sei in persistence[x]:
        s = filtration[sei.index]    # simplex
        cycle_edges.append((points[s[0]], points[s[1]]))

    # selected_point = diagram[index]
    # cycle = persistence[selected_point.index]
    # cycle_points = np.array([points[simplex[0]] for simplex in cycle if len(simplex) == 1])
    # return cycle_points
    return np.array(cycle_edges), (pt.birth, pt.death)

# Initialize session state
if "points" not in st.session_state:
    st.session_state.num_points = 30
    st.session_state.points = np.random.rand(st.session_state.num_points, 3)
if "diagram" not in st.session_state:
    st.session_state.diagram = None
if "persistence" not in st.session_state:
    st.session_state.persistence = None

# Title
st.title("3D Alpha Complex and Persistence Diagram Viewer")

# Sidebar for user input
num_points = st.sidebar.number_input(
    "Number of Points",
    min_value=10,
    max_value=1000,
    value=st.session_state.num_points,
    step=10,
    key="num_points_input"
)

# Buttons for regenerating points and choosing diagram index
if st.button("Regenerate Points"):
    st.session_state.num_points = num_points
    st.session_state.points = np.random.rand(st.session_state.num_points, 3)
    st.session_state.diagram = None
    st.session_state.persistence = None

if "selected_index" not in st.session_state:
    st.session_state.selected_index = 0

selected_index = st.number_input(
    "Choose Persistence Diagram Point Index",
    min_value=0,
    value=st.session_state.selected_index,
    step=1,
    format="%d",
    key="selected_index_input",
)

st.session_state.selected_index = int(selected_index)

# Generate the alpha complex and persistence diagram if not already computed
if st.session_state.diagram is None or st.session_state.persistence is None:
    points = st.session_state.points
    alpha_complex = diode.fill_alpha_shapes(points)
    filtration = dio.Filtration(alpha_complex)
    persistence = dio.homology_persistence(filtration)
    diagram = dio.init_diagrams(persistence, filtration)
    tmp = []
    for i in range(len(diagram[1])):
        tmp.append((i,diagram[1][i].death/diagram[1][i].birth)) 
    sorted_index = [j[0] for j in sorted(tmp, key=lambda x: x[1], reverse=True)]
    st.session_state.sorted_index = sorted_index
    st.session_state.persistence = persistence
    st.session_state.diagram = diagram
    st.session_state.filtration = filtration

points = st.session_state.points
diagram = st.session_state.diagram
persistence = st.session_state.persistence
filtration = st.session_state.filtration
sorted_index = st.session_state.sorted_index
# Plot the 3D points
fig_3d_points = go.Figure()
fig_3d_points.add_trace(go.Scatter3d(
    x=points[:, 0],
    y=points[:, 1],
    z=points[:, 2],
    mode='markers',
    marker=dict(size=2, color='blue'),
    name='Points'
))


fig_3d_points.update_layout(title="3D Points", scene=dict(aspectmode='data'), showlegend=False)
# Plot the persistence diagram with highlighted point
fig_diagram = go.Figure()
dimension = 1  # Fixed to homological dimension 1
highlighted_birth = None
highlighted_death = None

if diagram and len(diagram) > dimension:
    births = [pt.birth for pt in diagram[dimension]]
    deaths = [pt.death for pt in diagram[dimension]]
    colors = ['red' if i == sorted_index[st.session_state.selected_index] else 'blue'
              for i in range(len(diagram[dimension]))]
    fig_diagram.add_trace(go.Scatter(
        x=births, y=deaths,
        mode='markers',
        marker=dict(size=4, color=colors),
        name=f"Dimension {dimension}"
    ))
    highlighted_birth = births[sorted_index[st.session_state.selected_index]]
    highlighted_death = deaths[sorted_index[st.session_state.selected_index]]

fig_diagram.update_layout(
    title="Persistence Diagram (Dimension 1)",
    xaxis_title="Birth",
    yaxis_title="Death",
    showlegend=False
)

# Show the 3D points and persistence diagram
col1, col2  = st.columns(2)
# with col1:
#     st.plotly_chart(fig_3d_points, use_container_width=True)
with col1:
    st.plotly_chart(fig_diagram, use_container_width=True)

        
# Get the representative cycle
if diagram and len(diagram) > dimension and len(diagram[dimension]) > st.session_state.selected_index:
    cycle_edges, (birth,death) = get_representative_cycle(persistence, filtration, diagram[dimension], points, sorted_index[st.session_state.selected_index])
    
    # Display the persistence birth and death
    st.write(f"Persistence Birth: {birth}, Death: {death} Ratio: {death/birth}")
  
    for edge in cycle_edges:
        fig_3d_points.add_trace(go.Scatter3d(
            x=[edge[0][0], edge[1][0]],
            y=[edge[0][1], edge[1][1]],
            z=[edge[0][2], edge[1][2]],
            mode='lines',
            line=dict(color='red', width=3)
        ))
   
    with col2:
        st.plotly_chart(fig_3d_points, use_container_width=True)

else:
    st.write("No representative cycle available for the selected index.")