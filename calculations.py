
#calculatin.py
# civileng.serdar@gmail.com
"""
Steel Cutting Optimization - LEXICOGRAPHIC (Sequential) Optimization
Priority #1: Minimize number of bars
Priority #2: Minimize waste (ONLY if more bars than theoretical minimum)

FIXED VERSION:
- Bug #1: Pattern generation now respects actual demand (counts)
- Bug #2: Waste percentage uses industry standard formula (waste / total_capacity)
"""

from ortools.linear_solver import pywraplp
import math
from typing import List, Tuple, Dict, Optional


def generate_comprehensive_patterns(
    lengths: List[float],
    counts: List[int],  # ← FIXED: Added counts parameter
    bin_capacity: float = 12.0, 
    min_efficiency: float = 0.85,
    max_patterns: int = 500,
    verbose: bool = False
) -> Tuple[List[List[int]], List[Dict]]:
    """
    Generate comprehensive pattern pool
    
    FIXED: All patterns now respect actual demand (counts parameter)
    FIXED: Smart efficiency handling for small orders
    
    Strategies:
    1. Single-type patterns
    2. Two-type combinations
    3. Three-type combinations (most common)
    4. Greedy fill patterns (maximum utilization)
    """
    n_types = len(lengths)
    max_per_type = [int(bin_capacity // l) for l in lengths]
    
    # FIXED: Limit patterns to actual demand
    max_needed = [min(max_per_type[i], counts[i]) for i in range(n_types)]
    
    # SMART EFFICIENCY: For small orders, relax efficiency constraint
    total_demand = sum(lengths[i] * counts[i] for i in range(n_types))
    demand_ratio = total_demand / bin_capacity
    
    # If demand is less than 50% of one bar, allow any efficiency
    effective_min_efficiency = min_efficiency
    if demand_ratio < 0.5:
        effective_min_efficiency = 0.0
        if verbose:
            print(f"  ℹ Small order detected ({demand_ratio*100:.1f}% of bar)")
            print(f"  → Efficiency constraint relaxed (any pattern accepted)")
    
    min_efficiency = effective_min_efficiency
    
    patterns = []
    pattern_info = []
    seen = set()
    
    # 1. Single-type patterns - FIXED: Use max_needed instead of max_per_type
    for i in range(n_types):
        for count in range(max_needed[i], 0, -1):  # ← FIXED: was max_per_type[i]
            combo = [0] * n_types
            combo[i] = count
            total = lengths[i] * count
            
            if total <= bin_capacity:
                waste = bin_capacity - total
                efficiency = total / bin_capacity
                
                if efficiency >= min_efficiency:
                    combo_tuple = tuple(combo)
                    if combo_tuple not in seen:
                        seen.add(combo_tuple)
                        patterns.append(combo)
                        pattern_info.append({
                            'pattern': combo_tuple,
                            'waste': waste,
                            'efficiency': efficiency,
                            'total': total
                        })
    
    # 2. Two-type combinations - FIXED: Use max_needed
    for i in range(n_types):
        for j in range(i, n_types):
            max_ci = min(max_needed[i], 10)  # ← FIXED: was max_per_type[i]
            max_cj = min(max_needed[j], 10) if i != j else max_ci  # ← FIXED
            
            for ci in range(1, max_ci + 1):
                for cj in range(1, max_cj + 1):
                    if i == j and ci >= cj:
                        continue
                    
                    combo = [0] * n_types
                    combo[i] = ci
                    if i != j:
                        combo[j] = cj
                    
                    total = sum(lengths[k] * combo[k] for k in range(n_types))
                    
                    if total <= bin_capacity:
                        waste = bin_capacity - total
                        efficiency = total / bin_capacity
                        
                        if efficiency >= min_efficiency and waste <= 1.5:
                            combo_tuple = tuple(combo)
                            if combo_tuple not in seen:
                                seen.add(combo_tuple)
                                patterns.append(combo)
                                pattern_info.append({
                                    'pattern': combo_tuple,
                                    'waste': waste,
                                    'efficiency': efficiency,
                                    'total': total
                                })
    
    # 3. Three-type combinations - FIXED: Use max_needed
    for i in range(n_types):
        for j in range(i + 1, n_types):
            for k in range(j + 1, n_types):
                max_ci = min(max_needed[i], 6)  # ← FIXED
                max_cj = min(max_needed[j], 6)  # ← FIXED
                max_ck = min(max_needed[k], 6)  # ← FIXED
                
                for ci in range(1, max_ci + 1):
                    for cj in range(1, max_cj + 1):
                        for ck in range(1, max_ck + 1):
                            combo = [0] * n_types
                            combo[i] = ci
                            combo[j] = cj
                            combo[k] = ck
                            
                            total = sum(lengths[m] * combo[m] for m in range(n_types))
                            
                            if total <= bin_capacity:
                                waste = bin_capacity - total
                                efficiency = total / bin_capacity
                                
                                if efficiency >= min_efficiency and waste <= 1.2:
                                    combo_tuple = tuple(combo)
                                    if combo_tuple not in seen:
                                        seen.add(combo_tuple)
                                        patterns.append(combo)
                                        pattern_info.append({
                                            'pattern': combo_tuple,
                                            'waste': waste,
                                            'efficiency': efficiency,
                                            'total': total
                                        })
    
    # 4. Greedy fill patterns - FIXED: Use max_needed
    sorted_indices = sorted(range(n_types), key=lambda x: lengths[x], reverse=True)
    
    for start_idx in sorted_indices[:min(3, n_types)]:
        max_start = min(max_needed[start_idx], 5)  # ← FIXED
        
        for main_count in range(1, max_start + 1):
            combo = [0] * n_types
            combo[start_idx] = main_count
            remaining = bin_capacity - lengths[start_idx] * main_count
            
            for fill_idx in reversed(sorted_indices):
                if fill_idx == start_idx:
                    continue
                if remaining >= lengths[fill_idx]:
                    # FIXED: Don't exceed what's needed
                    fit_count = int(remaining // lengths[fill_idx])
                    needed_count = max_needed[fill_idx] - combo[fill_idx]
                    actual_count = min(fit_count, needed_count)
                    
                    combo[fill_idx] = actual_count
                    remaining -= lengths[fill_idx] * actual_count
            
            total = sum(lengths[m] * combo[m] for m in range(n_types))
            waste = bin_capacity - total
            efficiency = total / bin_capacity
            
            if efficiency >= min_efficiency:
                combo_tuple = tuple(combo)
                if combo_tuple not in seen:
                    seen.add(combo_tuple)
                    patterns.append(combo)
                    pattern_info.append({
                        'pattern': combo_tuple,
                        'waste': waste,
                        'efficiency': efficiency,
                        'total': total
                    })
    
    # Sort by waste and take best N patterns
    combined = list(zip(patterns, pattern_info))
    combined.sort(key=lambda x: (x[1]['waste'], -x[1]['efficiency']))
    
    if len(combined) > max_patterns:
        combined = combined[:max_patterns]
    
    patterns = [c[0] for c in combined]
    pattern_info = [c[1] for c in combined]
    
    if verbose:
        print(f"  → {len(patterns)} patterns generated")
    
    return patterns, pattern_info


def solve_phase1_minimize_bins(
    lengths: List[float],
    counts: List[int],
    patterns: List[List[int]],
    pattern_info: List[Dict],
    bin_capacity: float = 12.0,
    time_limit_ms: int = 30000,
    verbose: bool = False
) -> Optional[Tuple[int, List[Dict], float]]:
    """
    PHASE 1: Minimize number of bars only
    """
    n_patterns = len(patterns)
    n_types = len(lengths)
    
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        solver = pywraplp.Solver.CreateSolver('CBC')
    
    y = {}
    for p in range(n_patterns):
        y[p] = solver.IntVar(0, solver.infinity(), f'pattern_{p}')
    
    # Demand constraints
    for t in range(n_types):
        solver.Add(
            sum(patterns[p][t] * y[p] for p in range(n_patterns)) >= counts[t]
        )
    
    # Objective: minimize number of bars ONLY
    total_bins = sum(y[p] for p in range(n_patterns))
    solver.Minimize(total_bins)
    
    solver.SetTimeLimit(time_limit_ms)
    status = solver.Solve()
    
    if status != pywraplp.Solver.OPTIMAL and status != pywraplp.Solver.FEASIBLE:
        return None
    
    min_bins = int(solver.Objective().Value())
    
    used_patterns = []
    total_waste_m = 0
    
    for p in range(n_patterns):
        count = int(y[p].solution_value())
        if count > 0:
            pattern_total = sum(patterns[p][i] * lengths[i] for i in range(n_types))
            pattern_waste = bin_capacity - pattern_total
            
            used_patterns.append({
                'pattern_id': p,
                'count': count,
                'combo': patterns[p],
                'waste': pattern_waste,
                'total': pattern_total
            })
            total_waste_m += pattern_waste * count
    
    if verbose:
        print(f"  → Minimum bars: {min_bins}")
        print(f"  → Total waste: {total_waste_m:.2f}m")
    
    return min_bins, used_patterns, total_waste_m


def solve_phase2_minimize_waste(
    lengths: List[float],
    counts: List[int],
    patterns: List[List[int]],
    pattern_info: List[Dict],
    fixed_bins: int,
    bin_capacity: float = 12.0,
    time_limit_ms: int = 30000,
    verbose: bool = False
) -> Optional[Tuple[List[Dict], float]]:
    """
    PHASE 2: Minimize waste with fixed number of bars
    """
    n_patterns = len(patterns)
    n_types = len(lengths)
    
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        solver = pywraplp.Solver.CreateSolver('CBC')
    
    y = {}
    for p in range(n_patterns):
        y[p] = solver.IntVar(0, solver.infinity(), f'pattern_{p}')
    
    # Demand constraints
    for t in range(n_types):
        solver.Add(
            sum(patterns[p][t] * y[p] for p in range(n_patterns)) >= counts[t]
        )
    
    # CRITICAL: Number of bars is FIXED
    solver.Add(sum(y[p] for p in range(n_patterns)) == fixed_bins)
    
    # Objective: minimize waste ONLY
    total_waste = sum(pattern_info[p]['waste'] * y[p] for p in range(n_patterns))
    solver.Minimize(total_waste)
    
    solver.SetTimeLimit(time_limit_ms)
    status = solver.Solve()
    
    if status != pywraplp.Solver.OPTIMAL and status != pywraplp.Solver.FEASIBLE:
        return None
    
    used_patterns = []
    total_waste_m = 0
    
    for p in range(n_patterns):
        count = int(y[p].solution_value())
        if count > 0:
            pattern_total = sum(patterns[p][i] * lengths[i] for i in range(n_types))
            pattern_waste = bin_capacity - pattern_total
            
            used_patterns.append({
                'pattern_id': p,
                'count': count,
                'combo': patterns[p],
                'waste': pattern_waste,
                'total': pattern_total
            })
            total_waste_m += pattern_waste * count
    
    if verbose:
        print(f"  → Optimized waste: {total_waste_m:.2f}m")
    
    return used_patterns, total_waste_m


def solve_with_lexicographic_optimization(
    lengths: List[float],
    counts: List[int],
    bin_capacity: float = 12.0,
    min_efficiency: float = 0.85,
    max_patterns: int = 500,
    phase1_time_limit_ms: int = 30000,
    phase2_time_limit_ms: int = 30000,
    verbose: bool = True,
    adaptive: bool = True
) -> Optional[Dict]:
    """
    Lexicographic (Sequential) Optimization - ADAPTIVE VERSION
    
    FIXED: Pattern generation respects counts, waste % uses correct formula
    
    Logic:
    1. PHASE 1: Find minimum number of bars
    2. DECISION: Compare with theoretical minimum
       - If theoretical = found → STOP (optimal!)
       - If theoretical < found → Go to PHASE 2
    3. PHASE 2: Minimize waste with fixed bars
    
    ADAPTIVE: Auto-reduce min_efficiency if no solution found
    """
    total_demand = sum(l * c for l, c in zip(lengths, counts))
    theoretical_min = math.ceil(total_demand / bin_capacity)
    
    # Check for cuts that are too long
    max_length = max(lengths)
    if max_length > bin_capacity:
        if verbose:
            print("\n" + "="*70)
            print("❌ WARNING: CUT TOO LONG DETECTED!")
            print("="*70)
            print(f"Longest cut: {max_length:.2f}m")
            print(f"Bar length: {bin_capacity}m")
            print(f"This cut doesn't fit in {bin_capacity}m bar!")
            print("Solution: Use welding/splice or longer bars.")
        return None
    
    if verbose:
        print("\n" + "="*70)
        print("LEXICOGRAPHIC OPTIMIZATION (ADAPTIVE) - FIXED VERSION")
        print("="*70)
        print(f"Total demand: {total_demand:.2f}m")
        print(f"Theoretical minimum: {theoretical_min} bars")
        print(f"Bar length: {bin_capacity}m")
    
    # SMART EFFICIENCY: For single-bar cases or small orders, relax efficiency
    adaptive_efficiency_levels = [min_efficiency]
    
    # If theoretical minimum is 1 bar, always include 0% efficiency
    if theoretical_min == 1:
        if verbose:
            print(f"ℹ Single-bar case detected → Efficiency constraint relaxed")
        adaptive_efficiency_levels = [0.0]  # Skip efficiency check entirely
        adaptive = False  # No need for adaptive
    elif adaptive:
        current = min_efficiency
        while current > 0.0:  # Go all the way to 0% if needed
            current -= 0.05
            adaptive_efficiency_levels.append(round(max(current, 0.0), 2))
    
    efficiency_levels = adaptive_efficiency_levels
    
    phase1_result = None
    patterns = None
    pattern_info = None
    used_efficiency = min_efficiency
    
    # Try each efficiency level
    for eff in efficiency_levels:
        if verbose and eff != efficiency_levels[0] and len(efficiency_levels) > 1:
            print(f"\n⚠ No solution found, reducing efficiency: {eff*100:.0f}%")
        
        if verbose and eff == efficiency_levels[0] and len(efficiency_levels) > 1:
            print("\n[PREPARATION] Generating pattern pool...")
        elif verbose and len(efficiency_levels) == 1:
            print("\n[PREPARATION] Generating pattern pool...")
        
        # FIXED: Pass counts parameter to pattern generator
        patterns, pattern_info = generate_comprehensive_patterns(
            lengths=lengths,
            counts=counts,  # ← FIXED: Now passes counts
            bin_capacity=bin_capacity,
            min_efficiency=eff,
            max_patterns=max_patterns,
            verbose=verbose and eff == efficiency_levels[0]
        )
        
        if not patterns:
            if verbose:
                print(f"  → No patterns found with {eff*100:.0f}% efficiency")
            continue
        
        if verbose:
            print(f"\n[PHASE 1] Calculating minimum bars (efficiency: {eff*100:.0f}%)...")
        
        phase1_result = solve_phase1_minimize_bins(
            lengths=lengths,
            counts=counts,
            patterns=patterns,
            pattern_info=pattern_info,
            bin_capacity=bin_capacity,
            time_limit_ms=phase1_time_limit_ms,
            verbose=verbose
        )
        
        if phase1_result is not None:
            used_efficiency = eff
            if verbose and eff != efficiency_levels[0] and len(efficiency_levels) > 1:
                print(f"  ✓ Solution found (efficiency: {eff*100:.0f}%)")
            break
    
    if phase1_result is None:
        if verbose:
            print("\n" + "="*70)
            print("❌ NO SOLUTION FOUND!")
            print("="*70)
            print("All efficiency levels tried but no solution found.")
            print("Possible reasons:")
            print("  1. Cut lengths create combinations that are too large")
            print("  2. Demand quantities incompatible with pattern combinations")
            print("Suggestions:")
            print("  1. Increase max_patterns (500 → 1000)")
            print("  2. Increase time limit (30s → 60s)")
            print("  3. Check bar length")
        return None
    
    min_bins, used_patterns, total_waste = phase1_result
    
    # CRITICAL DECISION: Compare with theoretical minimum
    if verbose:
        print(f"\n[DECISION ANALYSIS]")
        print(f"  Theoretical minimum: {theoretical_min} bars")
        print(f"  Found minimum: {min_bins} bars")
        if used_efficiency != efficiency_levels[0]:
            print(f"  ⚠ Found with reduced efficiency: {used_efficiency*100:.0f}%")
        elif used_efficiency == 0.0 and theoretical_min == 1:
            print(f"  ℹ Single-bar case: efficiency constraint bypassed")
    
    if min_bins == theoretical_min:
        # OPTIMAL! No need for Phase 2
        if verbose:
            print(f"  ✓ OPTIMAL! At theoretical minimum!")
            print(f"  → Skipping Phase 2 (unnecessary)")
        
        final_patterns = used_patterns
        final_waste = total_waste
        phase_used = 1
    
    else:
        # More than theoretical - Try to improve with Phase 2
        if verbose:
            print(f"  ⚠ {min_bins - theoretical_min} bars more than theoretical")
            print(f"  → Proceeding to Phase 2 (waste optimization)")
        
        if verbose:
            print(f"\n[PHASE 2] Bars={min_bins} fixed, minimizing waste...")
        
        phase2_result = solve_phase2_minimize_waste(
            lengths=lengths,
            counts=counts,
            patterns=patterns,
            pattern_info=pattern_info,
            fixed_bins=min_bins,
            bin_capacity=bin_capacity,
            time_limit_ms=phase2_time_limit_ms,
            verbose=verbose
        )
        
        if phase2_result is None:
            if verbose:
                print("  ⚠ Phase 2 failed, using Phase 1 result")
            final_patterns = used_patterns
            final_waste = total_waste
            phase_used = 1
        else:
            final_patterns, final_waste = phase2_result
            phase_used = 2
            
            if verbose:
                improvement = total_waste - final_waste
                print(f"  ✓ Waste improvement: {improvement:.2f}m")
    
    # FIXED: Use industry standard formula for waste percentage
    total_capacity = min_bins * bin_capacity
    waste_percentage = (final_waste / total_capacity) * 100  # ← FIXED: was (final_waste / total_demand)
    
    if verbose:
        print("\n" + "="*70)
        print("RESULT SUMMARY")
        print("="*70)
        print(f"Bars used: {min_bins}")
        print(f"Total capacity: {total_capacity:.2f}m")
        print(f"Total waste: {final_waste:.2f}m")
        print(f"Waste percentage: {waste_percentage:.2f}% (of total capacity)")  # ← FIXED: clarified
        print(f"Phase used: {phase_used}")
        if used_efficiency == 0.0 and theoretical_min == 1:
            print(f"ℹ Efficiency: Not applicable (single-bar small order)")
        elif used_efficiency != efficiency_levels[0]:
            print(f"⚠ Reduced efficiency: {used_efficiency*100:.0f}% (initial: {efficiency_levels[0]*100:.0f}%)")
    
    return {
        'used_patterns': final_patterns,
        'total_bins': min_bins,
        'total_waste': final_waste,
        'waste_percentage': waste_percentage,
        'theoretical_min': theoretical_min,
        'total_demand': total_demand,
        'total_capacity': total_capacity,  # ← FIXED: Added for clarity
        'phase_used': phase_used,
        'used_efficiency': used_efficiency
    }


def print_results(
    result: Dict,
    lengths: List[float],
    bin_capacity: float = 12.0
):
    """Print results"""
    print("\n" + "="*70)
    print("USED PATTERNS")
    print("="*70)
    
    used_patterns_sorted = sorted(result['used_patterns'], key=lambda x: x['waste'])
    
    n_types = len(lengths)
    for up in used_patterns_sorted:
        pattern_str = ' + '.join([f"{up['combo'][i]}x{lengths[i]}m" 
                                 for i in range(n_types) if up['combo'][i] > 0])
        
        calculated_total = sum(up['combo'][i] * lengths[i] for i in range(n_types))
        calculated_waste = bin_capacity - calculated_total
        
        print(f"\n{up['count']} bars → {pattern_str}")
        print(f"  Total: {calculated_total:.2f}m | Waste: {calculated_waste:.2f}m | "
              f"Utilization: {(calculated_total/bin_capacity)*100:.1f}%")


def solve_packing_lexicographic(
    lengths: List[float],
    counts: List[int],
    bin_capacity: float = 12.0,
    min_efficiency: float = 0.85,
    max_patterns: int = 500,
    phase1_time_limit_ms: int = 30000,
    phase2_time_limit_ms: int = 30000,
    verbose: bool = True,
    print_output: bool = True,
    adaptive: bool = True
) -> Optional[Dict]:
    """
    Lexicographic optimization - Main function
    """
    if len(lengths) != len(counts):
        raise ValueError("lengths and counts must have same length!")
    
    if verbose:
        print("\n" + "="*70)
        print("INPUT INFORMATION")
        print("="*70)
        total_demand = sum(l * c for l, c in zip(lengths, counts))
        print(f"Total demand: {total_demand:.2f}m")
        print(f"Bar length: {bin_capacity}m")
        print(f"Number of cut types: {len(lengths)}")
    
    result = solve_with_lexicographic_optimization(
        lengths=lengths,
        counts=counts,
        bin_capacity=bin_capacity,
        min_efficiency=min_efficiency,
        max_patterns=max_patterns,
        phase1_time_limit_ms=phase1_time_limit_ms,
        phase2_time_limit_ms=phase2_time_limit_ms,
        verbose=verbose,
        adaptive=adaptive
    )
    
    if result and print_output:
        print_results(result, lengths, bin_capacity)
    
    return result


def solve_multi_diameter_lexicographic(
    demands: Dict[int, Dict],
    bin_capacity: float = 12.0,
    min_efficiency: float = 0.85,
    max_patterns: int = 1000,
    phase1_time_limit_ms: int = 90000,
    phase2_time_limit_ms: int = 90000,
    verbose: bool = True,
    print_output: bool = True,
    adaptive: bool = True
) -> Dict[int, Optional[Dict]]:
    """
    Lexicographic optimization for multi-diameter steel
    
    Args:
        demands: {diameter: {'lengths': [...], 'counts': [...]}}
        adaptive: Auto-reduce efficiency (recommended: True)
    
    Returns:
        {diameter: result_dict}
    """
    if not demands:
        raise ValueError("demands cannot be empty!")
    
    results = {}
    
    for diameter in sorted(demands.keys()):
        demand_data = demands[diameter]
        
        if 'lengths' not in demand_data or 'counts' not in demand_data:
            raise ValueError(f"'lengths' and 'counts' required for diameter {diameter}mm!")
        
        if print_output:
            print("\n" + "="*80)
            print(f"DIAMETER: {diameter}mm")
            print("="*80)
        
        current_bin_capacity = demand_data.get('bin_capacity', bin_capacity)
        
        result = solve_packing_lexicographic(
            lengths=demand_data['lengths'],
            counts=demand_data['counts'],
            bin_capacity=current_bin_capacity,
            min_efficiency=min_efficiency,
            max_patterns=max_patterns,
            phase1_time_limit_ms=phase1_time_limit_ms,
            phase2_time_limit_ms=phase2_time_limit_ms,
            verbose=verbose,
            print_output=print_output,
            adaptive=adaptive
        )
        
        results[diameter] = result
    
    # Overall summary - FIXED: Use correct waste percentage formula
    if print_output:
        print("\n" + "="*80)
        print("OVERALL SUMMARY - ALL DIAMETERS (FIXED VERSION)")
        print("="*80)
        
        total_bins_all = 0
        total_waste_all = 0
        total_capacity_all = 0  # ← FIXED: Track total capacity
        total_demand_all = 0
        
        print(f"\n{'DIAM(mm)':<12} {'BARS':<10} {'WASTE(m)':<12} {'WASTE%':<10} "
              f"{'DEMAND(m)':<12} {'PHASE':<8} {'EFFIC':<8}")
        print("-" * 85)
        
        for diameter in sorted(results.keys()):
            result = results[diameter]
            if result:
                effic_str = f"{result.get('used_efficiency', min_efficiency)*100:.0f}%"
                print(f"{diameter:<12} {result['total_bins']:<10} "
                      f"{result['total_waste']:<12.2f} "
                      f"{result['waste_percentage']:<10.2f} "
                      f"{result['total_demand']:<12.2f} "
                      f"{result['phase_used']:<8} "
                      f"{effic_str:<8}")
                
                total_bins_all += result['total_bins']
                total_waste_all += result['total_waste']
                total_capacity_all += result['total_capacity']  # ← FIXED
                total_demand_all += result['total_demand']
            else:
                print(f"{diameter:<12} {'NO SOLUTION':<10}")
        
        print("-" * 85)
        
        # FIXED: Use correct formula for overall waste percentage
        avg_waste_pct = (total_waste_all / total_capacity_all * 100) if total_capacity_all > 0 else 0
        
        print(f"{'TOTAL':<12} {total_bins_all:<10} "
              f"{total_waste_all:<12.2f} "
              f"{avg_waste_pct:<10.2f} "
              f"{total_demand_all:<12.2f}")
        print(f"\nTotal capacity: {total_capacity_all:.2f}m ({total_bins_all} bars × {bin_capacity}m)")
        print("="*85)
        print("\n✓ FIXED: Waste % = (Total Waste / Total Capacity) × 100")
        print(f"  = ({total_waste_all:.2f}m / {total_capacity_all:.2f}m) × 100")
        print(f"  = {avg_waste_pct:.2f}%")
    
    return results