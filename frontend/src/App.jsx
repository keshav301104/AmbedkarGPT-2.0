import { useState, useEffect, useRef, useCallback } from 'react'
import axios from 'axios'
import ForceGraph2D from 'react-force-graph-2d'
import ReactMarkdown from 'react-markdown'
import { Send, Activity, Share2, BookOpen, User, Bot, Layers, FileText, RotateCcw, Cpu, Network, Focus } from 'lucide-react'

function App() {
  // --- STATE MANAGEMENT ---
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Jai Bhim! I am AmbedkarGPT. Ask me about the Caste System, Social Democracy, or the Constitution.' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  
  // Data States
  const [fullGraph, setFullGraph] = useState({ nodes: [], links: [] }) 
  const [currentGraph, setCurrentGraph] = useState({ nodes: [], links: [] }) 
  const [metrics, setMetrics] = useState({ confidence: 0, source_count: 0 })
  const [contextData, setContextData] = useState({ local: [], global: [] }) 
  const [containerDimensions, setContainerDimensions] = useState({ width: 800, height: 600 });
  
  // UI States
  const [activeTab, setActiveTab] = useState('graph') 
  const chatEndRef = useRef(null)
  const graphRef = useRef()
  const containerRef = useRef()

  // --- EFFECTS ---

  // 1. Initial Load & Resize Listener
  useEffect(() => {
    fetchFullGraph();
    
    const updateDimensions = () => {
      if (containerRef.current) {
        setContainerDimensions({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight
        });
      }
    };

    window.addEventListener('resize', updateDimensions);
    updateDimensions(); // Initial measure
    
    return () => window.removeEventListener('resize', updateDimensions);
  }, [])

  // 2. Dynamic Visual Centering (The Fix)
  useEffect(() => {
    if (graphRef.current) {
      // Apply Physics
      graphRef.current.d3Force('charge').strength(-120);
      graphRef.current.d3Force('link').distance(70);
      
      // Calculate Shift: Move UP by 20% of screen height to clear the bottom panel
      const verticalShift = containerDimensions.height * 0.2;
      
      // Force Center
      graphRef.current.centerAt(0, verticalShift, 600); 
      graphRef.current.zoomToFit(400, 50);

      // Double-check after physics settles
      setTimeout(() => {
        if(graphRef.current) {
            graphRef.current.centerAt(0, verticalShift, 600);
            graphRef.current.zoomToFit(500, 50);
        }
      }, 1000);
    }
  }, [currentGraph, activeTab, containerDimensions]);

  // 3. Auto-scroll Chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // --- API HANDLERS ---
  const fetchFullGraph = () => {
    axios.get('http://127.0.0.1:8000/graph')
      .then(res => {
        setFullGraph(res.data);
        setCurrentGraph(res.data);
      })
      .catch(err => console.error(err))
  }

  const handleSend = async () => {
    if (!input.trim()) return

    const userMsg = { role: 'user', text: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await axios.post('http://127.0.0.1:8000/chat', { query: userMsg.text })
      
      const botMsg = { role: 'bot', text: res.data.answer }
      setMessages(prev => [...prev, botMsg])
      setMetrics(res.data.metrics)
      setContextData(res.data.context) 

      if (res.data.graph_data.nodes.length > 0) {
        setCurrentGraph(res.data.graph_data)
        setActiveTab('graph') 
      }
      
    } catch (error) {
      setMessages(prev => [...prev, { role: 'bot', text: "Error: Could not reach the Knowledge Engine." }])
    }
    setLoading(false)
  }

  // --- CUSTOM GRAPH PAINTING ---
  const paintNode = useCallback((node, ctx, globalScale) => {
    const label = node.id;
    const fontSize = 14/globalScale;
    
    // Draw Glow
    const glowSize = node.val ? node.val * 1.5 : 8;
    ctx.beginPath();
    ctx.arc(node.x, node.y, glowSize, 0, 2 * Math.PI, false);
    ctx.fillStyle = 'rgba(56, 189, 248, 0.2)';
    ctx.fill();

    // Draw Core
    ctx.beginPath();
    ctx.arc(node.x, node.y, 4, 0, 2 * Math.PI, false);
    ctx.fillStyle = '#38bdf8'; 
    ctx.fill();

    // Draw Label
    if (globalScale > 1.2 || node.degree > 3) {
      ctx.font = `${fontSize}px Sans-Serif`;
      const textWidth = ctx.measureText(label).width;
      const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.4); 

      ctx.fillStyle = 'rgba(15, 23, 42, 0.9)'; 
      ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2 - 12, bckgDimensions[0], bckgDimensions[1]);

      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#e2e8f0'; 
      ctx.fillText(label, node.x, node.y - 12);
    }
  }, []);

  return (
    <div className="flex h-screen overflow-hidden font-sans text-slate-800">
      
      {/* --- LEFT PANEL: Chat (55%) --- */}
      <div className="w-[55%] flex flex-col border-r border-slate-200 bg-white shadow-xl z-10 relative">
        <header className="p-4 border-b border-slate-100 flex items-center gap-3 bg-white">
          <div className="p-2 bg-ambedkar-800 rounded-lg text-white">
            <BookOpen size={20} />
          </div>
          <div>
            <h1 className="font-bold text-lg text-slate-800">AmbedkarGPT</h1>
            <p className="text-[10px] text-slate-500 font-medium uppercase tracking-wide">SemRAG v2.0</p>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8 space-y-8 bg-slate-50">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              
              {/* Custom Avatar Logic */}
              <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-md overflow-hidden border border-slate-200 ${
                msg.role === 'user' ? 'bg-slate-200' : 'bg-white'
              }`}>
                {msg.role === 'user' ? (
                  <User size={20} className="text-slate-600"/>
                ) : (
                  <img src="/ambedkar.jpg" alt="Bot" className="w-full h-full object-cover" />
                )}
              </div>
              
              <div className={`max-w-[85%] p-5 rounded-2xl text-base leading-relaxed shadow-sm ${
                msg.role === 'user' 
                  ? 'bg-ambedkar-800 text-white rounded-tr-none' 
                  : 'bg-white text-slate-700 border border-slate-200 rounded-tl-none'
              }`}>
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              </div>
            </div>
          ))}
          {loading && <div className="text-sm text-slate-400 animate-pulse ml-14">Retrieving Context & Generating Graph...</div>}
          <div ref={chatEndRef} />
        </div>

        <div className="p-6 bg-white border-t border-slate-100">
          <div className="flex gap-2 bg-slate-50 p-3 rounded-xl border border-slate-200 focus-within:ring-2 ring-ambedkar-500/20 shadow-inner">
            <input 
              className="flex-1 bg-transparent border-none outline-none px-3 text-base"
              placeholder="Ask a question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <button onClick={handleSend} disabled={loading} className="p-3 bg-ambedkar-800 text-white rounded-lg hover:bg-ambedkar-900 transition-colors">
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* --- RIGHT PANEL: Dashboard (45%) --- */}
      <div className="w-[45%] bg-slate-950 flex flex-col relative border-l border-slate-800">
        
        {/* Top Bar */}
        <div className="h-14 border-b border-slate-800 flex items-center justify-between px-6 bg-slate-900/50 backdrop-blur-sm z-20">
           <div className="flex gap-2 bg-slate-800 p-1 rounded-lg border border-slate-700">
              <button 
                onClick={() => setActiveTab('graph')}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-[11px] font-bold uppercase transition-all ${
                  activeTab === 'graph' ? 'bg-ambedkar-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
                }`}
              >
                <Network size={14} /> Knowledge Graph
              </button>
              <button 
                onClick={() => setActiveTab('evidence')}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-[11px] font-bold uppercase transition-all ${
                  activeTab === 'evidence' ? 'bg-ambedkar-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
                }`}
              >
                <FileText size={14} /> Evidence
              </button>
           </div>
        </div>

        {/* CONTENT */}
        <div className="flex-1 relative overflow-hidden" ref={containerRef}>
          
          {/* VIEW 1: GRAPH */}
          <div className={`absolute inset-0 transition-opacity duration-500 ${activeTab === 'graph' ? 'opacity-100 z-10' : 'opacity-0 z-0'}`}>
             <ForceGraph2D
               ref={graphRef}
               width={containerDimensions.width} 
               height={containerDimensions.height} 
               graphData={currentGraph}
               nodeCanvasObject={paintNode}
               linkColor={() => "rgba(148, 163, 184, 0.2)"} 
               backgroundColor="#020617" 
               
               // PARTICLES
               linkDirectionalParticles={2}
               linkDirectionalParticleSpeed={0.005}
               linkDirectionalParticleWidth={2}
               linkDirectionalParticleColor={() => "#38bdf8"}
               
               // PHYSICS & CENTERING
               d3AlphaDecay={0.01}
               d3VelocityDecay={0.4}
               cooldownTicks={100} 
               onEngineStop={() => {
                   const shift = containerDimensions.height * 0.2;
                   graphRef.current.centerAt(0, shift, 600);
                   graphRef.current.zoomToFit(400, 50);
               }} 
             />
             
             {/* Bottom Overlay */}
             <div className="absolute bottom-6 left-6 right-6 bg-slate-900/80 backdrop-blur-xl p-4 rounded-xl border border-slate-800 flex items-center justify-between shadow-2xl">
                <div className="flex items-center gap-4">
                    <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-400 border border-indigo-500/20">
                        <Cpu size={20} />
                    </div>
                    <div>
                        <h3 className="text-white font-bold text-xs uppercase tracking-wide">Graph State</h3>
                        <p className="text-[10px] text-slate-400">
                           {currentGraph.nodes.length} Active Nodes
                        </p>
                    </div>
                </div>
                
                <div className="flex items-center gap-4 text-xs border-l border-slate-700 pl-6">
                    <div>
                        <span className="block text-slate-500 font-bold text-[10px] uppercase">Confidence</span>
                        <span className="text-emerald-400 font-mono text-base">{(metrics.confidence * 100).toFixed(0)}%</span>
                    </div>
                    
                    <div className="flex gap-2">
                      <button 
                        onClick={() => {
                             const shift = containerDimensions.height * 0.2;
                             graphRef.current.centerAt(0, shift, 600);
                             graphRef.current.zoomToFit(400, 50);
                        }}
                        className="bg-slate-800 hover:bg-slate-700 text-white p-2 rounded-lg border border-slate-600 transition-colors"
                        title="Re-Center Graph"
                      >
                        <Focus size={16} />
                      </button>
                      <button 
                        onClick={() => { setCurrentGraph(fullGraph); setTimeout(() => graphRef.current.zoomToFit(400, 50), 100); }}
                        className="bg-slate-800 hover:bg-slate-700 text-white p-2 rounded-lg border border-slate-600 transition-colors"
                        title="Reset Graph"
                      >
                        <RotateCcw size={16} />
                      </button>
                    </div>
                </div>
             </div>
          </div>

          {/* VIEW 2: EVIDENCE */}
          <div className={`absolute inset-0 overflow-y-auto p-8 bg-slate-950 transition-opacity duration-300 ${activeTab === 'evidence' ? 'opacity-100 z-10' : 'opacity-0 z-0'}`}>
             <div className="max-w-xl mx-auto space-y-8 pb-20">
                
                {/* Local Context */}
                <div>
                   <h3 className="text-ambedkar-500 text-[10px] font-bold uppercase tracking-widest mb-4 flex items-center gap-2">
                     <Share2 size={14}/> Local Context (Specifics)
                   </h3>
                   <div className="space-y-3">
                     {contextData.local.length > 0 ? contextData.local.map((item, i) => (
                       <div key={i} className="bg-slate-900 p-4 rounded-lg border border-slate-800 text-slate-300 text-sm leading-relaxed shadow-sm hover:border-ambedkar-500/30 transition-colors">
                          <span className="text-ambedkar-400 font-mono text-[10px] mb-2 block border-b border-slate-800 pb-1">MATCH SCORE: {item.score.toFixed(2)}</span>
                          "{item.text}"
                       </div>
                     )) : <p className="text-slate-600 text-sm italic">No specific text found.</p>}
                   </div>
                </div>

                {/* Global Context */}
                <div>
                   <h3 className="text-emerald-500 text-[10px] font-bold uppercase tracking-widest mb-4 flex items-center gap-2">
                     <Layers size={14}/> Global Context (Themes)
                   </h3>
                   <div className="space-y-3">
                     {contextData.global.length > 0 ? contextData.global.map((item, i) => (
                       <div key={i} className="bg-slate-900/50 p-4 rounded-lg border border-slate-800 text-slate-400 text-sm italic shadow-sm hover:border-emerald-500/30 transition-colors">
                          <span className="text-emerald-600 font-mono text-[10px] mb-2 block border-b border-slate-800 pb-1">COMMUNITY SUMMARY</span>
                          "{item.text}"
                       </div>
                     )) : <p className="text-slate-600 text-sm italic">No thematic summaries found.</p>}
                   </div>
                </div>

             </div>
          </div>

        </div>
      </div>
    </div>
  )
}

export default App