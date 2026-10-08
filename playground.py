import time
import binomial, binary, sequential, commander, product

def run_benchmark():
    # Sử dụng các kích thước vừa phải để thu số liệu nhanh
    board_sizes = [4, 8, 12, 16] 
    methods = {
        'Binomial': binomial,
        'Binary': binary,
        'Sequential': sequential,
        'Commander': commander,
        'Product': product
    }

    print(f"{'N':<5} | {'Encoding':<12} | {'Time (s)':<10} | {'Variables':<10} | {'Clauses':<10}")
    print("-" * 60)

    for n in board_sizes:
        for name, module in methods.items():
            start_time = time.time()
            solution, vars_count, clauses_count = module.solve_n_queens(n)
            elapsed_time = time.time() - start_time
            
            if solution:
                print(f"{n:<5} | {name:<12} | {elapsed_time:<10.4f} | {vars_count:<10} | {clauses_count:<10}")
            else:
                print(f"{n:<5} | {name:<12} | {'TIMEOUT/ERR':<10} | {'-':<10} | {'-':<10}")
        print("-" * 60)

if __name__ == "__main__":
    run_benchmark()