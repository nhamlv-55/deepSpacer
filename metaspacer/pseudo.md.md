
# Table of Contents



In C code

    lbool context::solve_core (unsigned from_lvl)
    {
        scoped_watch _w_(m_solve_watch);
        //if there is no query predicate, abort
        if (!m_rels.find(m_query_pred, m_query)) { return l_false; }
    
        unsigned lvl = from_lvl;
    
        pob *root = m_query->mk_pob(nullptr,from_lvl,0,m.mk_true());
        m_pob_queue.set_root (*root);
    
        unsigned max_level = m_max_level;
    
        for (unsigned i = from_lvl; i < max_level; ++i) {
            checkpoint();
            m_expanded_lvl = infty_level ();
            m_stats.m_max_query_lvl = lvl;
    
            if (check_reachability()) { return l_true; }
    
            if (lvl > 0 && m_use_propagate)
                if (propagate(m_expanded_lvl, lvl, UINT_MAX)) { dump_json(); return l_false; }
    
            //push same information to database
    
            dump_json();
    
            if (is_inductive()){
                return l_false;
            }
    
            for (unsigned i = 0; i < m_callbacks.size(); i++){
                if (m_callbacks[i]->unfold())
                    m_callbacks[i]->unfold_eh();
            }
    
            m_pob_queue.inc_level ();
            lvl = m_pob_queue.max_level ();
            m_stats.m_max_depth = std::max(m_stats.m_max_depth, lvl);
            IF_VERBOSE(1,verbose_stream() << "Entering level "<< lvl << "\n";);
    
            STRACE("spacer_progress", tout << "\n* LEVEL " << lvl << "\n";);
            // push to a central database
            IF_VERBOSE(1,
                       if (m_params.print_statistics ()) {
                           statistics st;
                           collect_statistics (st);
                       };
                );
    
        }
        // communicate failure to datalog::context
        if (m_context) { m_context->set_status(datalog::BOUNDED); }
        return l_undef;
    }

    #----------query-------------
    def execute(..., timeout = -1):
    
    
    #----------solver------------
    def solve(filename):
      CHC = ms.CHCProblem(filename)
      Q = ms.query(CHC)
      query = CHC.queries[0]
      checkpoint = 10
      level = 0
      suggestion = list[] #a list of lemmas
      trigger(server, filename) #notice the server that we gonna work on this problem
      while True:
        res, _ = Q.execute(query, from = level, to = level+checkpoint)
        if res == "sat" or res == "unsat":
          break
        new_suggestion = request(server, filename)
        if len(new_suggestion) > len(suggestion):
          Q.add_lemmas(new_suggestion - suggestion) 
        level+=checkpoint
      done(server, filename)
    
    #-----------server-------------
    oracles = {} #each chc file has its own oracle. if down the line we realize that 1 for all chc formulas is good enough, nothing has to be changed.
    worker_pool = []
    def handle_request(filename):
      return (select guess from DB.output where res=="sat")
    
    def handle_trigger(filename):
      if filename not in models:
        oracles[filename] = oracle(filename)
        worker_pool.append(oracle.main_loop())
    def handle_done(filename):
      remove_all_data(filename)
    
    #-----------oracle--------------
    def __init__(self, filename):
      self.filename = filename
      self.data = []
      self.net = ...
      self.no_of_predictions = 10 #how many predictions we want to try after training
      self.timeout = 1000
      self.worker_pool = []
    def main_loop(self):
      while True:
        n = (select count(*) from DB.data where DB.data.filename = filename) #detect whether new data has been added
        if n>len(self.data):
          self.data = (select * from DB.data where DB.data.filename = filename)
          self.past_guess = (select * from DB.output where DB.output.filename = filename)
          train(self.data, self.past_guess) #self.net is train and update here
          for i in range(no_of_predictions):
            #try the prediction for a limited amount of time
            self.worker_pool.append(predict(timeout))
    
    def predict(self, timeout):
      input = self.data
      output = self.net.forward(input)
      if (select res from DB.output where DB.output.guess = output) is None: #if the guess hasn't been checked
        lemmas  = [i["lemmas"] for i in input]
        CHC = ms.CHCProblem(self.filename, lemmas)
        Q = ms.query(CHC)
        query = output
        res, _ = Q.execute(query, timeout)
        (insert filename, output, res to DB.output)

\#DB schema
DB.data

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<tbody>
<tr>
<td class="org-left">filename</td>
<td class="org-left">level</td>
<td class="org-left">pob</td>
<td class="org-left">lemmas</td>
<td class="org-left">stat</td>
</tr>
</tbody>
</table>

DB.output

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<tbody>
<tr>
<td class="org-left">filename</td>
<td class="org-left">guess</td>
<td class="org-left">res</td>
</tr>
</tbody>
</table>

